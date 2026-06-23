class FeedItem {
  final String id;
  final String imageUrl;
  final String universe;

  const FeedItem({required this.id, required this.imageUrl, required this.universe});

  factory FeedItem.fromJson(Map<String, dynamic> json) => FeedItem(
        id: json['id'] as String,
        imageUrl: json['image_url'] as String,
        universe: json['universe'] as String? ?? '',
      );
}
