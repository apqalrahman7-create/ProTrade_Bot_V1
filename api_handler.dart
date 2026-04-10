import 'package:http/http.dart' as http;
import 'dart:convert';

class ApiHandler {
  final String baseUrl = "http://YOUR_SERVER_IP:5000";

  // دالة تشغيل البوت لمدة 12 ساعة
  Future<Map<String, dynamic>> startTrading(String apiKey, String apiSecret, String exchange) async {
    final response = await http.post(
      Uri.parse('$baseUrl/start_bot'),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        "api_key": apiKey,
        "api_secret": apiSecret,
        "exchange": exchange,
        "symbol": "BTC/USDT"
      }),
    );
    return jsonDecode(response.body);
  }

  // دالة جلب الأرباح الحالية (الـ 5 دولار) والوقت
  Future<Map<String, dynamic>> getLiveStatus(int sessionId) async {
    final response = await http.get(Uri.parse('$baseUrl/get_status/$sessionId'));
    return jsonDecode(response.body);
  }
}
