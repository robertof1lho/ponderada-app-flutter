import 'package:shared_preferences/shared_preferences.dart';

const _keyToken = 'auth_token';
const _keyUserId = 'auth_user_id';

class AuthService {
  static String? _token;
  static String? _userId;

  static String? get token => _token;
  static String? get userId => _userId;
  static bool get isLoggedIn => _token != null;

  static Future<void> save(String userId, String token) async {
    _userId = userId;
    _token = token;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keyToken, token);
    await prefs.setString(_keyUserId, userId);
  }

  static Future<void> load() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString(_keyToken);
    _userId = prefs.getString(_keyUserId);
  }

  static Future<void> clear() async {
    _token = null;
    _userId = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_keyToken);
    await prefs.remove(_keyUserId);
  }
}
