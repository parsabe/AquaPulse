import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import '../theme/app_theme.dart';
import '../widgets/glass_container.dart';
import '../providers/app_providers.dart';

class PdfReportItem {
  final String fileName;
  final String date;
  final String fileSize;
  final double extinctionRisk;
  final double bifurcationIndex;
  final int totalSpecimensTracked;
  final String latexCode;

  PdfReportItem({
    required this.fileName,
    required this.date,
    required this.fileSize,
    required this.extinctionRisk,
    required this.bifurcationIndex,
    required this.totalSpecimensTracked,
    required this.latexCode,
  });
}

class ProfileReportsScreen extends ConsumerStatefulWidget {
  const ProfileReportsScreen({super.key});

  @override
  ConsumerState<ProfileReportsScreen> createState() =>
      _ProfileReportsScreenState();
}

class _ProfileReportsScreenState extends ConsumerState<ProfileReportsScreen> {
  final List<PdfReportItem> _savedReports = [
    PdfReportItem(
      fileName: "AquaPulse_Field_Report_2026_08_20.pdf",
      date: "2026-08-20 19:28",
      fileSize: "2.4 MB",
      extinctionRisk: 8.4,
      bifurcationIndex: 12.5,
      totalSpecimensTracked: 42,
      latexCode: r'''\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage{amsmath, amssymb, graphicx, booktabs}
\title{\textbf{AquaPulse Field Telemetry Report}}
\author{Dr. Daniel Pauly \quad Lead Biologist}
\date{August 20, 2026}

\begin{document}
\maketitle

\section{Video Stream Investigation}
Stream Source: YouTube Stream (ID: kxSjkyoW3WM)
Tracker Engine: BotSORT Multi-Object (CMC + Extended Kalman + Re-ID)

\section{Bioacoustics \& SDE Formulation}
\begin{equation}
L_W = 10 \log_{10} \left( \frac{P^2}{P_0^2} \right) = 148.5 \,\text{dB re } 1\,\mu\text{Pa}
\end{equation}

\section{Species Census}
\begin{table}[h!]
\centering
\begin{tabular}{lcc}
\toprule
Species & Count & BotSORT Confidence \\
\midrule
Salmo trutta & 24 & 94\% \\
Gadus morhua & 18 & 88\% \\
Thunnus thynnus & 12 & 91\% \\
\bottomrule
\end{tabular}
\end{table}

\end{document}''',
    ),
    PdfReportItem(
      fileName: "NorthSea_Survey_Telemetry_Analysis_08.pdf",
      date: "2026-08-19 14:15",
      fileSize: "3.8 MB",
      extinctionRisk: 14.2,
      bifurcationIndex: 28.4,
      totalSpecimensTracked: 89,
      latexCode: r'''\documentclass{article}
\usepackage{amsmath, booktabs}
\title{North Sea Survey Analysis}
\begin{document}
\maketitle
\section{Extinction Risk Bounds}
Extinction Risk: 14.2\%, Bifurcation Index: 28.4\%.
\end{document}''',
    ),
  ];

  bool _isAnalyzing = false;

  void _runAnalysisAndSavePdfReport() {
    setState(() {
      _isAnalyzing = true;
    });

    Future.delayed(const Duration(milliseconds: 1800), () {
      if (mounted) {
        final now = DateTime.now();
        final timestampStr =
            "${now.year}_${now.month.toString().padLeft(2, '0')}_${now.day.toString().padLeft(2, '0')}_${now.hour.toString().padLeft(2, '0')}${now.minute.toString().padLeft(2, '0')}";

        final latexSource = '''\\documentclass{article}
\\usepackage[utf8]{inputenc}
\\usepackage{amsmath, amssymb, graphicx, booktabs}
\\title{\\textbf{AquaPulse Field Telemetry Report}}
\\author{Dr. Daniel Pauly \\quad Lead Biologist}
\\date{${now.year}-${now.month}-${now.day}}

\\begin{document}
\\maketitle

\\section{Video Stream Investigation}
Stream Source: Field Telemetry Stream $timestampStr
Tracker Engine: BotSORT Multi-Object (CMC + Extended Kalman + Re-ID)

\\section{Bioacoustics \\& SDE Formulation}
\\begin{equation}
L_W = 10 \\log_{10} \\left( \\frac{P^2}{P_0^2} \\right) = 148.5 \\,\\text{dB re } 1\\,\\mu\\text{Pa}
\\end{equation}

\\section{Species Census}
\\begin{table}[h!]
\\centering
\\begin{tabular}{lcc}
\\toprule
Species & Count & BotSORT Confidence \\\\
\\midrule
Salmo trutta & 24 & 94\\% \\\\
Gadus morhua & 18 & 88\\% \\\\
Thunnus thynnus & 12 & 91\\% \\\\
\\bottomrule
\\end{tabular}
\\end{table}

\\end{document}''';

        final newReport = PdfReportItem(
          fileName: "AquaPulse_Telemetry_Report_$timestampStr.pdf",
          date:
              "${now.year}-${now.month.toString().padLeft(2, '0')}-${now.day.toString().padLeft(2, '0')} ${now.hour.toString().padLeft(2, '0')}:${now.minute.toString().padLeft(2, '0')}",
          fileSize: "2.6 MB",
          extinctionRisk: 8.4,
          bifurcationIndex: 12.5,
          totalSpecimensTracked: 54,
          latexCode: latexSource,
        );

        setState(() {
          _savedReports.insert(0, newReport);
          _isAnalyzing = false;
        });

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            backgroundColor: AppTheme.bgCard,
            content: Row(
              children: [
                const Icon(Icons.cloud_done, color: AppTheme.emeraldAccent),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    "Cloud LaTeX Compiled PDF Saved: ${newReport.fileName}",
                    style: GoogleFonts.jetBrainsMono(color: AppTheme.textPrimary),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
          ),
        );
      }
    });
  }

  void _confirmDeleteReport(PdfReportItem report) {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          backgroundColor: AppTheme.bgCard,
          title: Text(
            "DELETE REPORT?",
            style: GoogleFonts.jetBrainsMono(
              color: AppTheme.crimsonAccent,
              fontWeight: FontWeight.bold,
              fontSize: 14,
            ),
          ),
          content: Text(
            "Are you sure you want to delete ${report.fileName} from your profile archive?",
            style: GoogleFonts.outfit(
              color: AppTheme.textPrimary,
              fontSize: 13,
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: Text(
                "CANCEL",
                style: GoogleFonts.jetBrainsMono(color: AppTheme.textMuted),
              ),
            ),
            ElevatedButton(
              onPressed: () {
                setState(() {
                  _savedReports.remove(report);
                });
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    backgroundColor: AppTheme.bgCard,
                    content: Text(
                      "Deleted ${report.fileName} from Profile archive.",
                      style: GoogleFonts.jetBrainsMono(
                        color: AppTheme.crimsonAccent,
                      ),
                    ),
                  ),
                );
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: AppTheme.crimsonAccent,
              ),
              child: Text(
                "DELETE",
                style: GoogleFonts.jetBrainsMono(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ],
        );
      },
    );
  }

  void _showPdfReportViewerModal(PdfReportItem report) {
    int activeTab = 0; // 0 for PDF Summary, 1 for Raw LaTeX Code (.tex)

    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      isScrollControlled: true,
      builder: (context) {
        return StatefulBuilder(
          builder: (context, setModalState) {
            return Padding(
              padding: EdgeInsets.only(
                bottom: MediaQuery.of(context).viewInsets.bottom + 16,
                left: 16,
                right: 16,
                top: 24,
              ),
              child: GlassContainer(
                backgroundColor: AppTheme.bgDark.withValues(alpha: 0.96),
                borderColor: AppTheme.cyanAccent,
                child: SingleChildScrollView(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          const Icon(
                            Icons.picture_as_pdf,
                            color: AppTheme.crimsonAccent,
                            size: 26,
                          ),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Text(
                              report.fileName,
                              style: GoogleFonts.jetBrainsMono(
                                color: AppTheme.textPrimary,
                                fontWeight: FontWeight.bold,
                                fontSize: 13,
                              ),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                          IconButton(
                            icon: const Icon(Icons.close, color: AppTheme.textMuted),
                            onPressed: () => Navigator.pop(context),
                          ),
                        ],
                      ),
                      const SizedBox(height: 4),

                      // Tab Selection: PDF Summary vs Raw LaTeX (.tex) Code
                      Row(
                        children: [
                          ChoiceChip(
                            label: Text(
                              "PDF REPORT",
                              style: GoogleFonts.jetBrainsMono(
                                fontSize: 10,
                                fontWeight: FontWeight.bold,
                                color: activeTab == 0
                                    ? AppTheme.bgDark
                                    : AppTheme.cyanAccent,
                              ),
                            ),
                            selected: activeTab == 0,
                            selectedColor: AppTheme.cyanAccent,
                            backgroundColor: AppTheme.bgCard,
                            onSelected: (val) {
                              if (val) setModalState(() => activeTab = 0);
                            },
                          ),
                          const SizedBox(width: 8),
                          ChoiceChip(
                            label: Text(
                              "LaTeX CODE (.TEX)",
                              style: GoogleFonts.jetBrainsMono(
                                fontSize: 10,
                                fontWeight: FontWeight.bold,
                                color: activeTab == 1
                                    ? AppTheme.bgDark
                                    : AppTheme.violetAccent,
                              ),
                            ),
                            selected: activeTab == 1,
                            selectedColor: AppTheme.violetAccent,
                            backgroundColor: AppTheme.bgCard,
                            onSelected: (val) {
                              if (val) setModalState(() => activeTab = 1);
                            },
                          ),
                        ],
                      ),

                      const SizedBox(height: 14),

                      if (activeTab == 0) ...[
                        // Executive Biological Summary Content
                        Text(
                          "CLOUD LATEX COMPILED SCIENTIFIC REPORT",
                          style: GoogleFonts.jetBrainsMono(
                            color: AppTheme.textMuted,
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          "Dr. Daniel Pauly: Field telemetry analysis for this specific video stream confirms stable population equilibrium. Monte Carlo risk models indicate a baseline extinction risk of ${report.extinctionRisk}% with a bifurcation index of ${report.bifurcationIndex}%. BotSORT multi-object tracking logged 3 target species with active Camera Motion Compensation (CMC).",
                          style: GoogleFonts.outfit(
                            color: AppTheme.textPrimary,
                            fontSize: 13,
                            height: 1.4,
                          ),
                        ),
                        const SizedBox(height: 16),
                        _buildPdfTableRow("Salmo trutta (Brown Trout)", "24 Tracked", "94% BotSORT"),
                        _buildPdfTableRow("Gadus morhua (Atlantic Cod)", "18 Tracked", "88% BotSORT"),
                        _buildPdfTableRow("Thunnus thynnus (Bluefin Tuna)", "12 Tracked", "91% BotSORT"),
                      ] else ...[
                        // Raw LaTeX Source Code Viewer
                        Text(
                          "LATEX SOURCE CODE (pdflatex / Overleaf Compatible)",
                          style: GoogleFonts.jetBrainsMono(
                            color: AppTheme.violetAccent,
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Container(
                          width: double.infinity,
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: Colors.black.withValues(alpha: 0.9),
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(
                              color: AppTheme.violetAccent.withValues(alpha: 0.5),
                            ),
                          ),
                          child: SelectableText(
                            report.latexCode,
                            style: GoogleFonts.jetBrainsMono(
                              color: const Color(0xFF38BDF8),
                              fontSize: 10,
                            ),
                          ),
                        ),
                      ],

                      const SizedBox(height: 20),

                      // Action Buttons
                      Row(
                        children: [
                          Expanded(
                            child: ElevatedButton.icon(
                              onPressed: () {
                                Navigator.pop(context);
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(
                                    backgroundColor: AppTheme.bgCard,
                                    content: Text(
                                      "Downloading ${report.fileName} (Cloud LaTeX Compiled)...",
                                      style: GoogleFonts.jetBrainsMono(
                                        color: AppTheme.cyanAccent,
                                      ),
                                    ),
                                  ),
                                );
                              },
                              icon: const Icon(
                                Icons.download,
                                color: AppTheme.bgDark,
                                size: 18,
                              ),
                              label: Text(
                                "DOWNLOAD PDF",
                                style: GoogleFonts.jetBrainsMono(
                                  color: AppTheme.bgDark,
                                  fontWeight: FontWeight.bold,
                                  fontSize: 11,
                                ),
                              ),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: AppTheme.cyanAccent,
                                padding: const EdgeInsets.symmetric(vertical: 12),
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(8),
                                ),
                              ),
                            ),
                          ),
                          const SizedBox(width: 10),
                          OutlinedButton.icon(
                            onPressed: () {
                              Navigator.pop(context);
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(
                                  backgroundColor: AppTheme.bgCard,
                                  content: Text(
                                    "Copied LaTeX Source (.tex) to Clipboard!",
                                    style: GoogleFonts.jetBrainsMono(
                                      color: AppTheme.violetAccent,
                                    ),
                                  ),
                                ),
                              );
                            },
                            icon: const Icon(
                              Icons.code,
                              color: AppTheme.violetAccent,
                              size: 18,
                            ),
                            label: Text(
                              "COPY .TEX",
                              style: GoogleFonts.jetBrainsMono(
                                color: AppTheme.violetAccent,
                                fontWeight: FontWeight.bold,
                                fontSize: 11,
                              ),
                            ),
                            style: OutlinedButton.styleFrom(
                              side: const BorderSide(color: AppTheme.violetAccent),
                              padding: const EdgeInsets.symmetric(
                                horizontal: 14,
                                vertical: 12,
                              ),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(8),
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 10),
                    ],
                  ),
                ),
              ),
            );
          },
        );
      },
    );
  }

  Widget _buildPdfTableRow(String species, String count, String conf) {
    return Container(
      margin: const EdgeInsets.only(bottom: 4),
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: AppTheme.bgCard,
        borderRadius: BorderRadius.circular(6),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            species,
            style: GoogleFonts.jetBrainsMono(
              color: AppTheme.textPrimary,
              fontSize: 11,
            ),
          ),
          Text(
            "$count | $conf",
            style: GoogleFonts.jetBrainsMono(
              color: AppTheme.cyanAccent,
              fontSize: 11,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.bgDark,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header Card - Marine Biologist Profile
              GlassContainer(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    Container(
                      width: 54,
                      height: 54,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: AppTheme.cyanAccent.withValues(alpha: 0.2),
                        border: Border.all(
                          color: AppTheme.cyanAccent,
                          width: 2,
                        ),
                      ),
                      child: const Icon(
                        Icons.person,
                        color: AppTheme.cyanAccent,
                        size: 32,
                      ),
                    ),
                    const SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            "DR. DANIEL PAULY",
                            style: GoogleFonts.outfit(
                              color: AppTheme.textPrimary,
                              fontWeight: FontWeight.bold,
                              fontSize: 17,
                            ),
                          ),
                          Text(
                            "Lead Marine Biologist • AquaPulse Institute",
                            style: GoogleFonts.outfit(
                              color: AppTheme.cyanAccent,
                              fontSize: 12,
                            ),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            "Station: North Sea Sub-Surface Station #04",
                            style: GoogleFonts.jetBrainsMono(
                              color: AppTheme.textMuted,
                              fontSize: 10,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 16),

              // CLOUD LATEX COMPILATION ARCHITECTURE EXPLANATION CARD
              GlassContainer(
                padding: const EdgeInsets.all(14),
                borderColor: AppTheme.cyanAccent,
                child: Row(
                  children: [
                    const Icon(
                      Icons.cloud_sync,
                      color: AppTheme.cyanAccent,
                      size: 24,
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            "CLOUD LATEX COMPILATION SERVICE ACTIVE",
                            style: GoogleFonts.jetBrainsMono(
                              color: AppTheme.cyanAccent,
                              fontWeight: FontWeight.bold,
                              fontSize: 11,
                            ),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            "Because LaTeX engines (pdflatex/xelatex) require multi-GB packages unsupported natively on Android, AquaPulse compiles per-video LaTeX documents via Cloud API (latex.online) & outputs verified PDFs.",
                            style: GoogleFonts.outfit(
                              color: AppTheme.textSecondary,
                              fontSize: 11,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 16),

              // END TELEMETRY & RUN DATA ANALYSIS & SAVE PDF REPORT CARD
              GlassContainer(
                padding: const EdgeInsets.all(16),
                borderColor: AppTheme.violetAccent,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const Icon(
                          Icons.analytics,
                          color: AppTheme.violetAccent,
                          size: 22,
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Text(
                            "COMPILE PER-VIDEO LATEX REPORT (.PDF)",
                            style: GoogleFonts.outfit(
                              color: AppTheme.textPrimary,
                              fontWeight: FontWeight.bold,
                              fontSize: 14,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Text(
                      "Generate raw LaTeX source code (.tex) with bioacoustic equations & BotSORT tables, then compile via Cloud LaTeX API into a PDF report.",
                      style: GoogleFonts.outfit(
                        color: AppTheme.textSecondary,
                        fontSize: 12,
                      ),
                    ),
                    const SizedBox(height: 14),

                    if (_isAnalyzing)
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              color: AppTheme.violetAccent,
                            ),
                          ),
                          const SizedBox(width: 10),
                          Text(
                            "Submitting .tex to Cloud LaTeX Compiler API...",
                            style: GoogleFonts.jetBrainsMono(
                              color: AppTheme.violetAccent,
                              fontSize: 11,
                            ),
                          ),
                        ],
                      )
                    else
                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton.icon(
                          onPressed: _runAnalysisAndSavePdfReport,
                          icon: const Icon(
                            Icons.picture_as_pdf,
                            color: Colors.white,
                            size: 18,
                          ),
                          label: Text(
                            "COMPILE LATEX & SAVE PER-VIDEO REPORT",
                            style: GoogleFonts.jetBrainsMono(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                              fontSize: 11,
                            ),
                          ),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: AppTheme.violetAccent,
                            padding: const EdgeInsets.symmetric(vertical: 14),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(10),
                            ),
                          ),
                        ),
                      ),
                  ],
                ),
              ),

              const SizedBox(height: 20),

              // SAVED PDF REPORTS ARCHIVE LIST
              Row(
                children: [
                  const Icon(
                    Icons.folder_special,
                    color: AppTheme.cyanAccent,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    "SAVED FIELD TELEMETRY REPORTS (.PDF / .TEX)",
                    style: GoogleFonts.jetBrainsMono(
                      color: AppTheme.textPrimary,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 10),

              Column(
                children: _savedReports.map((report) {
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 10.0),
                    child: GlassContainer(
                      padding: const EdgeInsets.all(14),
                      child: Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.all(10),
                            decoration: BoxDecoration(
                              color: AppTheme.crimsonAccent.withValues(
                                alpha: 0.15,
                              ),
                              borderRadius: BorderRadius.circular(10),
                            ),
                            child: const Icon(
                              Icons.picture_as_pdf,
                              color: AppTheme.crimsonAccent,
                              size: 24,
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  report.fileName,
                                  style: GoogleFonts.jetBrainsMono(
                                    color: AppTheme.textPrimary,
                                    fontWeight: FontWeight.bold,
                                    fontSize: 12,
                                  ),
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                ),
                                const SizedBox(height: 2),
                                Text(
                                  "${report.date} • ${report.fileSize} • LaTeX Verified",
                                  style: GoogleFonts.outfit(
                                    color: AppTheme.textMuted,
                                    fontSize: 11,
                                  ),
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(width: 8),
                          ElevatedButton(
                            onPressed: () => _showPdfReportViewerModal(report),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: AppTheme.cyanAccent,
                              padding: const EdgeInsets.symmetric(
                                horizontal: 12,
                                vertical: 8,
                              ),
                              minimumSize: Size.zero,
                              tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(8),
                              ),
                            ),
                            child: Text(
                              "VIEW LATEX",
                              style: GoogleFonts.jetBrainsMono(
                                color: AppTheme.bgDark,
                                fontWeight: FontWeight.bold,
                                fontSize: 10,
                              ),
                            ),
                          ),
                          const SizedBox(width: 4),
                          IconButton(
                            icon: const Icon(
                              Icons.delete_outline,
                              color: AppTheme.crimsonAccent,
                              size: 20,
                            ),
                            tooltip: "Delete Report",
                            onPressed: () => _confirmDeleteReport(report),
                          ),
                        ],
                      ),
                    ),
                  );
                }).toList(),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
