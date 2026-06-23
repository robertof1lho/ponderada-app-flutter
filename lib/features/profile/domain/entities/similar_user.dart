class SimilarUser {
  final String userId;
  final int sharedStyles;
  const SimilarUser({required this.userId, required this.sharedStyles});

  factory SimilarUser.fromJson(Map<String, dynamic> json) => SimilarUser(
        userId: json['user_id'] as String,
        sharedStyles: (json['shared_styles'] as num).toInt(),
      );
}
