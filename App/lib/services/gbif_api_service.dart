import 'package:dio/dio.dart';
import '../models/taxonomy_model.dart';
import 'database_service.dart';

class GbifApiService {
  final Dio _dio = Dio(BaseOptions(
    connectTimeout: const Duration(seconds: 4),
    receiveTimeout: const Duration(seconds: 4),
  ));

  Future<TaxonomyModel?> fetchAndCacheSpecies(String speciesName) async {
    try {
      final response = await _dio.get(
        'https://api.gbif.org/v1/species/match',
        queryParameters: {'name': speciesName},
      );

      if (response.statusCode == 200 && response.data != null) {
        final data = response.data as Map<String, dynamic>;
        final usageKey = data['usageKey'] as int? ?? 0;
        final scientificName = data['scientificName'] as String? ?? speciesName;
        final family = data['family'] as String? ?? 'Aquatic Organism';
        final classTitle = data['class'] as String? ?? 'Actinopterygii';

        String imageUrl = "https://images.unsplash.com/photo-1544551763-46a013bb70d5?q=80&w=400";
        
        // Try fetching media from GBIF
        if (usageKey > 0) {
          try {
            final mediaRes = await _dio.get('https://api.gbif.org/v1/species/$usageKey/media');
            if (mediaRes.statusCode == 200 && mediaRes.data != null) {
              final results = mediaRes.data['results'] as List?;
              if (results != null && results.isNotEmpty) {
                for (var item in results) {
                  if (item['type'] == 'StillImage' && item['identifier'] != null) {
                    imageUrl = item['identifier'].toString();
                    break;
                  }
                }
              }
            }
          } catch (_) {}
        }

        final model = TaxonomyModel(
          gbifId: usageKey > 0 ? usageKey : DateTime.now().millisecondsSinceEpoch % 1000000,
          scientificName: scientificName,
          commonName: speciesName,
          family: family,
          classTitle: classTitle,
          iucnStatus: "LC",
          referenceImageUrl: imageUrl,
          censusCount: 1,
          habitatDescription: "Remote field oceanographic survey specimen.",
          isCachedOffline: true,
        );

        await DatabaseService.instance.saveTaxonomy(model);
        return model;
      }
    } catch (e) {
      // Offline fallback
    }
    return null;
  }
}
