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
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                "FIELD OFFLINE TAXONOMY CACHE",
                                style: GoogleFonts.outfit(
                                  color: AppTheme.textPrimary,
                                  fontWeight: FontWeight.bold,
                                  fontSize: 14,
                                ),
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                              Text(
                                "SQLite DB | GBIF Taxonomy & Census",
                                style: GoogleFonts.jetBrainsMono(
                                  color: AppTheme.textSecondary,
                                  fontSize: 10,
                                ),
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(width: 6),
                        Flexible(
                          child: Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 8,
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
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                const Icon(
                                  Icons.wifi_off,
                                  color: AppTheme.emeraldAccent,
                                  size: 10,
                                ),
                                const SizedBox(width: 4),
                                Flexible(
                                  child: Text(
                                    "OFFLINE READY",
                                    style: GoogleFonts.jetBrainsMono(
                                      color: AppTheme.emeraldAccent,
                                      fontWeight: FontWeight.bold,
                                      fontSize: 9,
                                    ),
                                    maxLines: 1,
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 14),

                    // Census Statistics Grid (Wrapped with Expanded to prevent overflow)
                    Row(
                      children: [
                        Expanded(
                          child: _buildStatChip(
                            "SPECIES CACHED",
                            "${speciesList.length}",
                            AppTheme.cyanAccent,
                          ),
                        ),
                        const SizedBox(width: 6),
                        Expanded(
                          child: _buildStatChip(
                            "TOTAL CENSUS",
                            "$totalCensus",
                            AppTheme.goldAccent,
                          ),
                        ),
                        const SizedBox(width: 6),
                        Expanded(
                          child: _buildStatChip(
                            "GBIF SYNC",
                            "LOCAL DB",
                            AppTheme.violetAccent,
                          ),
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
                        hintText: "Search GBIF (e.g. Salmo trutta)...",
                        hintStyle: GoogleFonts.outfit(
                          color: AppTheme.textMuted,
                          fontSize: 12,
                        ),
                        filled: true,
                        fillColor: AppTheme.bgCard,
                        contentPadding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 10,
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
                  const SizedBox(width: 8),
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
                        horizontal: 12,
                        vertical: 12,
                      ),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    child: isSyncing
                        ? const SizedBox(
                            width: 14,
                            height: 14,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              color: Colors.black,
                            ),
                          )
                        : Text(
                            "SYNC GBIF",
                            style: GoogleFonts.jetBrainsMono(
                              fontWeight: FontWeight.bold,
                              fontSize: 10,
                            ),
                          ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 12),

            // Cached Species Inventory Cards List
            Expanded(
              child: speciesList.isEmpty
                  ? Center(
                      child: Text(
                        "NO TAXONOMY DATA CACHED IN LOCAL SQLITE",
                        style: GoogleFonts.jetBrainsMono(
                          color: AppTheme.textMuted,
                          fontSize: 12,
                        ),
                      ),
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      itemCount: speciesList.length,
                      itemBuilder: (context, index) {
                        final species = speciesList[index];
                        return Padding(
                          padding: const EdgeInsets.only(bottom: 10.0),
                          child: GlassContainer(
                            padding: const EdgeInsets.all(12),
                            child: Row(
                              children: [
                                ClipRRect(
                                  borderRadius: BorderRadius.circular(10),
                                  child: Image.network(
                                    species.referenceImageUrl,
                                    width: 52,
                                    height: 52,
                                    fit: BoxFit.cover,
                                    errorBuilder: (context, error, stackTrace) {
                                      return Container(
                                        width: 52,
                                        height: 52,
                                        color: AppTheme.cyanAccent.withValues(
                                          alpha: 0.15,
                                        ),
                                        child: const Icon(
                                          Icons.set_meal,
                                          color: AppTheme.cyanAccent,
                                          size: 24,
                                        ),
                                      );
                                    },
                                  ),
                                ),
                                const SizedBox(width: 12),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        species.scientificName,
                                        style: GoogleFonts.outfit(
                                          color: AppTheme.textPrimary,
                                          fontWeight: FontWeight.bold,
                                          fontSize: 14,
                                        ),
                                        maxLines: 1,
                                        overflow: TextOverflow.ellipsis,
                                      ),
                                      Text(
                                        "${species.commonName} • Key: ${species.gbifId}",
                                        style: GoogleFonts.outfit(
                                          color: AppTheme.cyanAccent,
                                          fontSize: 11,
                                        ),
                                        maxLines: 1,
                                        overflow: TextOverflow.ellipsis,
                                      ),
                                      const SizedBox(height: 2),
                                      Text(
                                        "Family: ${species.family} | Habitat: ${species.habitatDescription}",
                                        style: GoogleFonts.jetBrainsMono(
                                          color: AppTheme.textMuted,
                                          fontSize: 9,
                                        ),
                                        maxLines: 1,
                                        overflow: TextOverflow.ellipsis,
                                      ),
                                    ],
                                  ),
                                ),
                                const SizedBox(width: 8),
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 10,
                                    vertical: 6,
                                  ),
                                  decoration: BoxDecoration(
                                    color: AppTheme.goldAccent.withValues(
                                      alpha: 0.15,
                                    ),
                                    borderRadius: BorderRadius.circular(8),
                                    border: Border.all(
                                      color: AppTheme.goldAccent,
                                    ),
                                  ),
                                  child: Column(
                                    children: [
                                      Text(
                                        "${species.censusCount}",
                                        style: GoogleFonts.jetBrainsMono(
                                          color: AppTheme.goldAccent,
                                          fontWeight: FontWeight.bold,
                                          fontSize: 14,
                                        ),
                                      ),
                                      Text(
                                        "LOGGED",
                                        style: GoogleFonts.jetBrainsMono(
                                          color: AppTheme.goldAccent,
                                          fontSize: 8,
                                        ),
                                      ),
                                    ],
                                  ),
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

  Widget _buildStatChip(String title, String value, Color color) {
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: GoogleFonts.jetBrainsMono(
              color: AppTheme.textMuted,
              fontSize: 8,
            ),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 2),
          Text(
            value,
            style: GoogleFonts.jetBrainsMono(
              color: color,
              fontWeight: FontWeight.bold,
              fontSize: 13,
            ),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }
}
