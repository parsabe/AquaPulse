import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:path/path.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';
import '../models/taxonomy_model.dart';

class DatabaseService {
  static final DatabaseService instance = DatabaseService._internal();
  static Database? _database;

  DatabaseService._internal();

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDatabase();
    return _database!;
  }

  Future<Database> _initDatabase() async {
    if (kIsWeb) {
      // In web fallback, handle memory / dummy database
      sqfliteFfiInit();
      databaseFactory = databaseFactoryFfi;
    } else if (defaultTargetPlatform == TargetPlatform.windows ||
        defaultTargetPlatform == TargetPlatform.linux ||
        defaultTargetPlatform == TargetPlatform.macOS) {
      sqfliteFfiInit();
      databaseFactory = databaseFactoryFfi;
    }

    final dbPath = await getDatabasesPath();
    final path = join(dbPath, 'aquapulse_field_taxonomy.db');

    return await openDatabase(path, version: 1, onCreate: _createDb);
  }

  Future<void> _createDb(Database db, int version) async {
    await db.execute('''
      CREATE TABLE taxonomy_cache (
        gbif_id INTEGER PRIMARY KEY,
        scientific_name TEXT NOT NULL,
        common_name TEXT NOT NULL,
        family TEXT NOT NULL,
        class_title TEXT NOT NULL,
        iucn_status TEXT NOT NULL,
        reference_image_url TEXT NOT NULL,
        census_count INTEGER NOT NULL,
        habitat_description TEXT NOT NULL,
        is_cached_offline INTEGER NOT NULL
      )
    ''');

    await db.execute('''
      CREATE TABLE alarm_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        alarm_type TEXT NOT NULL,
        extinction_risk REAL NOT NULL,
        bifurcation_index REAL NOT NULL,
        details TEXT NOT NULL
      )
    ''');

    // Seed default baseline GBIF marine taxonomy data for zero-latency offline field use
    await _seedDefaultTaxonomy(db);
  }

  Future<void> _seedDefaultTaxonomy(Database db) async {
    final List<TaxonomyModel> defaultSpecies = [
      TaxonomyModel(
        gbifId: 2386861,
        scientificName: "Salmo trutta",
        commonName: "Brown Trout",
        family: "Salmonidae",
        classTitle: "Actinopterygii",
        iucnStatus: "LC",
        referenceImageUrl:
            "https://images.unsplash.com/photo-1544551763-46a013bb70d5?q=80&w=400",
        censusCount: 42,
        habitatDescription: "Boreal cold-water rivers and coastal sea-runs.",
      ),
      TaxonomyModel(
        gbifId: 2415788,
        scientificName: "Gadus morhua",
        commonName: "Atlantic Cod",
        family: "Gadidae",
        classTitle: "Actinopterygii",
        iucnStatus: "VU",
        referenceImageUrl:
            "https://images.unsplash.com/photo-1524704654690-b56c05c78a00?q=80&w=400",
        censusCount: 28,
        habitatDescription:
            "Demersal coastal and shelf waters of North Atlantic.",
      ),
      TaxonomyModel(
        gbifId: 2413110,
        scientificName: "Thunnus thynnus",
        commonName: "Atlantic Bluefin Tuna",
        family: "Scombridae",
        classTitle: "Actinopterygii",
        iucnStatus: "EN",
        referenceImageUrl:
            "https://images.unsplash.com/photo-1508873696983-2df515122519?q=80&w=400",
        censusCount: 14,
        habitatDescription:
            "Pelagic oceanic waters, rapid migratory endurance predator.",
      ),
      TaxonomyModel(
        gbifId: 5218786,
        scientificName: "Chelonia mydas",
        commonName: "Green Sea Turtle",
        family: "Cheloniidae",
        classTitle: "Reptilia",
        iucnStatus: "EN",
        referenceImageUrl:
            "https://images.unsplash.com/photo-1518467166778-b88f373ffec7?q=80&w=400",
        censusCount: 9,
        habitatDescription:
            "Tropical and subtropical coastal reefs and seagrass meadows.",
      ),
      TaxonomyModel(
        gbifId: 2420684,
        scientificName: "Hippocampus hippocampus",
        commonName: "Short-snouted Seahorse",
        family: "Syngnathidae",
        classTitle: "Actinopterygii",
        iucnStatus: "DD",
        referenceImageUrl:
            "https://images.unsplash.com/photo-1544551763-46a013bb70d5?q=80&w=400",
        censusCount: 6,
        habitatDescription: "Shallow coastal estuarine eelgrass habitats.",
      ),
    ];

    for (var sp in defaultSpecies) {
      await db.insert(
        'taxonomy_cache',
        sp.toMap(),
        conflictAlgorithm: ConflictAlgorithm.replace,
      );
    }
  }

  Future<List<TaxonomyModel>> getAllTaxonomy() async {
    final db = await instance.database;
    final maps = await db.query('taxonomy_cache', orderBy: 'census_count DESC');
    return maps.map((m) => TaxonomyModel.fromMap(m)).toList();
  }

  Future<void> saveTaxonomy(TaxonomyModel taxonomy) async {
    final db = await instance.database;
    await db.insert(
      'taxonomy_cache',
      taxonomy.toMap(),
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  Future<void> updateCensusCount(String scientificName, int increment) async {
    final db = await instance.database;
    await db.rawUpdate(
      '''
      UPDATE taxonomy_cache SET census_count = census_count + ? WHERE scientific_name = ?
    ''',
      [increment, scientificName],
    );
  }

  Future<void> logAlarmEvent(
    String alarmType,
    double extinctionRisk,
    double bifurcationIndex,
    String details,
  ) async {
    final db = await instance.database;
    await db.insert('alarm_history', {
      'timestamp': DateTime.now().toIso8601String(),
      'alarm_type': alarmType,
      'extinction_risk': extinctionRisk,
      'bifurcation_index': bifurcationIndex,
      'details': details,
    });
  }

  Future<List<Map<String, dynamic>>> getAlarmLogs() async {
    final db = await instance.database;
    return await db.query('alarm_history', orderBy: 'id DESC', limit: 30);
  }
}
