import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import '../theme/app_theme.dart';
import '../widgets/glass_container.dart';
import '../providers/app_providers.dart';

class OfflineTaxonomyScreen extends ConsumerStatefulWidget {
  const OfflineTaxonomyScreen({super.key});

  @override
  ConsumerState<OfflineTaxonomyScreen> createState() =>
      _OfflineTaxonomyScreenState();
}

class _OfflineTaxonomyScreenState extends ConsumerState<OfflineTaxonomyScreen> {
  final TextEditingController _searchController = TextEditingController();
  bool isSyncing = false;

  @override
  Widget build(BuildContext context) {
    final speciesList = ref.watch(taxonomyProvider);
    final totalCensus = speciesList.fold<int>(
      0,
      (sum, item) => sum + item.censusCount,
    );

    return Scaffold(
      backgroundColor: AppTheme.bgDark,
      body: SafeArea(
        child: Column(
          children: [
            // Screen Header Bar
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: GlassContainer(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const Icon(
                          Icons.storage,
                          color: AppTheme.cyanAccent,
                          size: 22,
                        ),
                        const SizedBox(width: 10),
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              "FIELD OFFLINE TAXONOMY CACHE",
                              style: GoogleFonts.outfit(
                                color: AppTheme.textPrimary,
                                fontWeight: FontWeight.bold,
                                fontSize: 16,
                              ),
                            ),
                            Text(
                              "SQLite Database | GBIF Taxonomy & Ecological Census",
                              style: GoogleFonts.jetBrainsMono(
                                color: AppTheme.textSecondary,
                                fontSize: 11,
                              ),
                            ),
                          ],
                        ),
                        const Spacer(),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 10,
                            vertical: 4,
                          ),
                          decoration: BoxDecoration(
                            color: AppTheme.emeraldAccent.withValues(
                              alpha: 0.15,
                            ),
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(color: AppTheme.emeraldAccent),
                          ),
                          child: Row(
                            children: [
                              const Icon(
                                Icons.wifi_off,
                                color: AppTheme.emeraldAccent,
                                size: 12,
                              ),
                              const SizedBox(width: 4),
                              Text(
                                "OFFLINE READY",
                                style: GoogleFonts.jetBrainsMono(
                                  color: AppTheme.emeraldAccent,
                                  fontWeight: FontWeight.bold,
                                  fontSize: 10,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 14),

                    // Census Statistics Grid
                    Row(
                      children: [
                        _buildStatChip(
                          "SPECIES CACHED",
                          "${speciesList.length}",
                          AppTheme.cyanAccent,
                        ),
                        const SizedBox(width: 8),
                        _buildStatChip(
                          "TOTAL CENSUS",
                          "$totalCensus",
                          AppTheme.goldAccent,
                        ),
                        const SizedBox(width: 8),
                        _buildStatChip(
                          "GBIF SYNC",
                          "LOCAL DB",
                          AppTheme.violetAccent,
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),

            // GBIF Search & Local SQLite Sync Bar
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16.0),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _searchController,
                      style: GoogleFonts.outfit(color: AppTheme.textPrimary),
                      decoration: InputDecoration(
                        hintText:
                            "Enter GBIF species name (e.g. Salmo trutta)...",
                        hintStyle: GoogleFonts.outfit(
                          color: AppTheme.textMuted,
                          fontSize: 13,
                        ),
                        filled: true,
                        fillColor: AppTheme.bgCard,
                        contentPadding: const EdgeInsets.symmetric(
                          horizontal: 16,
                          vertical: 12,
                        ),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide: BorderSide(
                            color: AppTheme.cyanAccent.withValues(alpha: 0.3),
                          ),
                        ),
                        enabledBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide: BorderSide(
                            color: AppTheme.cyanAccent.withValues(alpha: 0.3),
                          ),
                        ),
                        focusedBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide: const BorderSide(
                            color: AppTheme.cyanAccent,
                            width: 1.5,
                          ),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),
                  ElevatedButton(
                    onPressed: isSyncing
                        ? null
                        : () async {
                            final text = _searchController.text.trim();
                            if (text.isNotEmpty) {
                              setState(() => isSyncing = true);
                              await ref
                                  .read(taxonomyProvider.notifier)
                                  .searchAndSyncSpecies(text);
                              _searchController.clear();
                              setState(() => isSyncing = false);
                            }
                          },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppTheme.cyanAccent,
                      foregroundColor: Colors.black,
                      padding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 14,
                      ),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    child: isSyncing
                        ? const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              color: Colors.black,
                            ),
                          )
                        : Text(
                            "SYNC GBIF",
                            style: GoogleFonts.jetBrainsMono(
                              fontWeight: FontWeight.bold,
                              fontSize: 12,
                            ),
                          ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 12),

            // Cached Taxonomy Cards List
            Expanded(
              child: speciesList.isEmpty
                  ? Center(
                      child: Text(
                        "No species in offline SQLite database.",
                        style: GoogleFonts.outfit(color: AppTheme.textMuted),
                      ),
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      itemCount: speciesList.length,
                      itemBuilder: (context, index) {
                        final species = speciesList[index];
                        return Padding(
                          padding: const EdgeInsets.only(bottom: 12.0),
                          child: GlassContainer(
                            padding: const EdgeInsets.all(12),
                            child: Row(
                              children: [
                                // Reference Species Image Thumbnail
                                ClipRRect(
                                  borderRadius: BorderRadius.circular(10),
                                  child: Image.network(
                                    species.referenceImageUrl,
                                    width: 72,
                                    height: 72,
                                    fit: BoxFit.cover,
                                    errorBuilder: (context, error, stackTrace) {
                                      return Container(
                                        width: 72,
                                        height: 72,
                                        color: AppTheme.bgCard,
                                        child: const Icon(
                                          Icons.image_not_supported,
                                          color: AppTheme.cyanAccent,
                                        ),
                                      );
                                    },
                                  ),
                                ),
                                const SizedBox(width: 14),

                                // Species Details
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Row(
                                        children: [
                                          Expanded(
                                            child: Text(
                                              species.scientificName,
                                              style: GoogleFonts.outfit(
                                                color: AppTheme.textPrimary,
                                                fontWeight: FontWeight.bold,
                                                fontSize: 15,
                                                fontStyle: FontStyle.italic,
                                              ),
                                            ),
                                          ),
                                          _buildIucnBadge(species.iucnStatus),
                                        ],
                                      ),
                                      const SizedBox(height: 2),
                                      Text(
                                        "${species.commonName} • ${species.family}",
                                        style: GoogleFonts.outfit(
                                          color: AppTheme.textSecondary,
                                          fontSize: 12,
                                        ),
                                      ),
                                      const SizedBox(height: 4),
                                      Text(
                                        species.habitatDescription,
                                        style: GoogleFonts.outfit(
                                          color: AppTheme.textMuted,
                                          fontSize: 11,
                                        ),
                                        maxLines: 1,
                                        overflow: TextOverflow.ellipsis,
                                      ),
                                    ],
                                  ),
                                ),

                                const SizedBox(width: 8),

                                // Census Count & Counter Button
                                Column(
                                  children: [
                                    Container(
                                      padding: const EdgeInsets.symmetric(
                                        horizontal: 10,
                                        vertical: 4,
                                      ),
                                      decoration: BoxDecoration(
                                        color: AppTheme.cyanAccent.withValues(
                                          alpha: 0.15,
                                        ),
                                        borderRadius: BorderRadius.circular(8),
                                        border: Border.all(
                                          color: AppTheme.cyanAccent.withValues(
                                            alpha: 0.5,
                                          ),
                                        ),
                                      ),
                                      child: Column(
                                        children: [
                                          Text(
                                            "${species.censusCount}",
                                            style: GoogleFonts.jetBrainsMono(
                                              color: AppTheme.cyanAccent,
                                              fontWeight: FontWeight.bold,
                                              fontSize: 16,
                                            ),
                                          ),
                                          Text(
                                            "COUNT",
                                            style: GoogleFonts.jetBrainsMono(
                                              color: AppTheme.textMuted,
                                              fontSize: 9,
                                            ),
                                          ),
                                        ],
                                      ),
                                    ),
                                    IconButton(
                                      icon: const Icon(
                                        Icons.add_circle_outline,
                                        color: AppTheme.goldAccent,
                                        size: 20,
                                      ),
                                      onPressed: () {
                                        ref
                                            .read(taxonomyProvider.notifier)
                                            .incrementCensus(
                                              species.scientificName,
                                            );
                                      },
                                    ),
                                  ],
                                ),
                              ],
                            ),
                          ),
                        );
                      },
                    ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatChip(String label, String value, Color color) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 10),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: color.withValues(alpha: 0.3)),
        ),
        child: Column(
          children: [
            Text(
              value,
              style: GoogleFonts.jetBrainsMono(
                color: color,
                fontWeight: FontWeight.bold,
                fontSize: 14,
              ),
            ),
            Text(
              label,
              style: GoogleFonts.jetBrainsMono(
                color: AppTheme.textMuted,
                fontSize: 9,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildIucnBadge(String status) {
    Color bg = AppTheme.emeraldAccent;
    if (status == 'VU') bg = AppTheme.goldAccent;
    if (status == 'EN' || status == 'CR') bg = AppTheme.crimsonAccent;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: bg.withValues(alpha: 0.2),
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: bg),
      ),
      child: Text(
        "IUCN: $status",
        style: GoogleFonts.jetBrainsMono(
          color: bg,
          fontWeight: FontWeight.bold,
          fontSize: 9,
        ),
      ),
    );
  }
}
