class AlterEgo {
  final String id;
  final String imageUrl;
  final List<String> styleTags;

  const AlterEgo({required this.id, required this.imageUrl, required this.styleTags});

  factory AlterEgo.fromJson(Map<String, dynamic> json) => AlterEgo(
        id: json['id'] as String,
        imageUrl: json['image_url'] as String,
        styleTags: (json['style_tags'] as List<dynamic>? ?? []).cast<String>(),
      );
}
