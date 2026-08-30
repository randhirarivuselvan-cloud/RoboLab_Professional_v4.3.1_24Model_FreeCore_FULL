import 'dart:convert';
import 'package:http/http.dart' as http;

class RoboLabApi {
  final String baseUrl;
  const RoboLabApi(this.baseUrl);

  Future<Map<String, dynamic>> health() async {
    final r = await http.get(Uri.parse('$baseUrl/health'));
    return _json(r);
  }

  Future<List<dynamic>> models() async {
    final r = await http.get(Uri.parse('$baseUrl/api/ai/models'));
    return (_json(r)['data'] as List<dynamic>);
  }

  Future<Map<String, dynamic>> runStage(String stage, String description, {String board = 'Arduino Uno', String language = 'Arduino C++'}) async {
    final r = await http.post(
      Uri.parse('$baseUrl/api/ai/$stage'),
      headers: {'content-type': 'application/json'},
      body: jsonEncode({'description': description, 'board': board, 'language': language, 'project': {}}),
    );
    return _json(r);
  }

  Future<Map<String, dynamic>> generateCode(String description, {String board = 'Arduino Uno', String language = 'Arduino C++'}) async {
    final r = await http.post(
      Uri.parse('$baseUrl/api/code/generate'),
      headers: {'content-type': 'application/json'},
      body: jsonEncode({'description': description, 'board': board, 'language': language}),
    );
    return _json(r);
  }

  Map<String, dynamic> _json(http.Response r) {
    final value = jsonDecode(r.body);
    if (r.statusCode < 200 || r.statusCode >= 300) {
      throw Exception('RoboLab API ${r.statusCode}: ${value is Map ? value['detail'] ?? value : value}');
    }
    return Map<String, dynamic>.from(value as Map);
  }
}
