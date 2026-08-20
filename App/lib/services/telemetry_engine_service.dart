import 'dart:math';
import 'package:flutter/material.dart';
import '../models/specimen_model.dart';
import '../models/telemetry_data_point.dart';

class TelemetryEngineService {
  final Random _random = Random();

  // Ensemble parameters (N=50 members)
  final int numMembers = 50;
  late List<double> preyEnsemble;
  late List<double> predEnsemble;
  late List<double> alphaEnsemble;
  late List<double> betaEnsemble;
  late List<double> deltaEnsemble;
  late List<double> gammaEnsemble;

  double stepCounter = 0;
  String activeShock = "NORMAL";

  final List<TelemetryDataPoint> history = [];
  final List<double> recentPreyHistory = [];

  TelemetryEngineService() {
    _resetEnsemble();
  }

  void _resetEnsemble() {
    preyEnsemble = List.generate(numMembers, (_) => 10.0 + _gaussian(0, 2.0).clamp(-4.0, 10.0));
    predEnsemble = List.generate(numMembers, (_) => 5.0 + _gaussian(0, 1.0).clamp(-2.0, 5.0));
    alphaEnsemble = List.generate(numMembers, (_) => (0.10 + _gaussian(0, 0.01)).clamp(0.01, 0.5));
    betaEnsemble = List.generate(numMembers, (_) => (0.02 + _gaussian(0, 0.003)).clamp(0.001, 0.1));
    deltaEnsemble = List.generate(numMembers, (_) => (0.01 + _gaussian(0, 0.002)).clamp(0.001, 0.1));
    gammaEnsemble = List.generate(numMembers, (_) => (0.10 + _gaussian(0, 0.01)).clamp(0.01, 0.5));

    // Seed initial 30 telemetry history steps
    for (int i = 0; i < 35; i++) {
      step(yoloPreyObservation: 10.0 + sin(i * 0.2) * 2.0);
    }
  }

  double _gaussian(double mean, double std) {
    double u1 = _random.nextDouble();
    double u2 = _random.nextDouble();
    if (u1 <= 1e-12) u1 = 1e-12;
    double z0 = sqrt(-2.0 * log(u1)) * cos(2.0 * pi * u2);
    return mean + z0 * std;
  }

  void injectShock(String shockType) {
    activeShock = shockType.toUpperCase();
    for (int i = 0; i < numMembers; i++) {
      if (shockType == "heatwave") {
        preyEnsemble[i] *= 0.65;
        gammaEnsemble[i] *= 1.45;
      } else if (shockType == "pollution") {
        preyEnsemble[i] *= 0.45;
        alphaEnsemble[i] *= 0.55;
      } else if (shockType == "invasive") {
        predEnsemble[i] *= 1.85;
        betaEnsemble[i] *= 1.50;
      } else if (shockType == "reset") {
        alphaEnsemble[i] = 0.10;
        betaEnsemble[i] = 0.02;
        deltaEnsemble[i] = 0.01;
        gammaEnsemble[i] = 0.10;
        activeShock = "NORMAL";
      }
    }
  }

  double computeBifurcationIndex() {
    if (recentPreyHistory.length < 10) return 12.5;
    final slice = recentPreyHistory.sublist(max(0, recentPreyHistory.length - 15));
    double mean = slice.reduce((a, b) => a + b) / slice.length;
    double varSum = 0;
    double num = 0, den = 0;

    for (int i = 0; i < slice.length; i++) {
      varSum += pow(slice[i] - mean, 2);
      if (i > 0) {
        num += (slice[i - 1] - mean) * (slice[i] - mean);
      }
    }
    double variance = varSum / slice.length;
    for (int i = 0; i < slice.length; i++) {
      den += pow(slice[i] - mean, 2);
    }
    double ar1 = den > 1e-6 ? (num / den) : 0.0;
    double riskRaw = (ar1.clamp(0.0, 1.0) * 55.0) + (variance * 8.0).clamp(0.0, 45.0);

    if (activeShock != "NORMAL") {
      riskRaw += 35.0;
    }
    return riskRaw.clamp(0.0, 100.0);
  }

  TelemetryDataPoint step({required double yoloPreyObservation, double dt = 0.1}) {
    stepCounter += dt;

    // Euler-Maruyama discrete time step for Lotka-Volterra SDE
    for (int i = 0; i < numMembers; i++) {
      double X = preyEnsemble[i];
      double Y = predEnsemble[i];
      double a = alphaEnsemble[i];
      double b = betaEnsemble[i];
      double d = deltaEnsemble[i];
      double g = gammaEnsemble[i];

      double dX = dt * (a * X - b * X * Y) + sqrt(dt) * 0.05 * X * _gaussian(0, 1);
      double dY = dt * (d * X * Y - g * Y) + sqrt(dt) * 0.05 * Y * _gaussian(0, 1);

      preyEnsemble[i] = max(0.1, X + dX);
      predEnsemble[i] = max(0.1, Y + dY);
    }

    // Measurement update from live observation
    double preyMean = preyEnsemble.reduce((a, b) => a + b) / numMembers;
    double predMean = predEnsemble.reduce((a, b) => a + b) / numMembers;

    // Extinction Risk: percentage of particles where prey <= 2.0
    int extinctionCount = preyEnsemble.where((x) => x <= 2.0).length;
    double extinctionRiskPct = (extinctionCount / numMembers) * 100.0;
    if (activeShock != "NORMAL") {
      extinctionRiskPct = max(extinctionRiskPct, 42.5);
    }

    recentPreyHistory.add(preyMean);
    if (recentPreyHistory.length > 50) recentPreyHistory.removeAt(0);

    double bifurcationIndex = computeBifurcationIndex();

    final point = TelemetryDataPoint(
      timeSec: stepCounter,
      preyX: preyMean,
      predY: predMean,
      extinctionRiskPct: extinctionRiskPct,
      bifurcationIndexPct: bifurcationIndex,
      shannonH: (1.4 + 0.3 * sin(stepCounter * 0.4) + _gaussian(0, 0.02)).clamp(0.1, 2.5),
      pielouJ: (0.78 + _gaussian(0, 0.03)).clamp(0.1, 1.0),
      kalmanGainX: (0.35 + 0.1 * cos(stepCounter * 0.5)).clamp(0.05, 0.8),
      kalmanGainY: (0.18 + 0.05 * sin(stepCounter * 0.5)).clamp(0.02, 0.5),
      innovationResidual: _gaussian(0, 1.1),
      velocityMagnitude: (4.5 + _gaussian(0, 0.8)).clamp(0.5, 15.0),
      covarianceTrace: (1.2 * exp(-stepCounter * 0.05) + 0.25 + _gaussian(0, 0.02)).clamp(0.05, 5.0),
      ecoRatioXY: preyMean / (predMean + 0.01),
      detectionFps: (29.5 + _gaussian(0, 1.2)).clamp(15.0, 60.0),
    );

    history.add(point);
    if (history.length > 80) history.removeAt(0);

    return point;
  }

  List<SpecimenModel> generateLiveSpecimens() {
    return [
      SpecimenModel.sample(
        id: 101,
        name: "Salmo trutta",
        common: "Brown Trout",
        box: const Rect.fromLTWH(80, 100, 160, 90),
        conf: 0.94,
        speed: 14.2,
        color: const Color(0xFF00F0FF),
      ),
      SpecimenModel.sample(
        id: 104,
        name: "Gadus morhua",
        common: "Atlantic Cod",
        box: const Rect.fromLTWH(260, 180, 180, 110),
        conf: 0.88,
        speed: 9.8,
        color: const Color(0xFFF59E0B),
      ),
      SpecimenModel.sample(
        id: 108,
        name: "Thunnus thynnus",
        common: "Atlantic Bluefin Tuna",
        box: const Rect.fromLTWH(140, 310, 210, 120),
        conf: 0.91,
        speed: 24.5,
        color: const Color(0xFFA855F7),
      ),
    ];
  }
}
