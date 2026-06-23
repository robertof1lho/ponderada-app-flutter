import 'package:dio/dio.dart';

String friendlyError(Object e) {
  if (e is DioException) {
    final status = e.response?.statusCode;
    final detail = e.response?.data is Map ? e.response?.data['detail'] : null;

    if (e.type == DioExceptionType.connectionTimeout ||
        e.type == DioExceptionType.receiveTimeout ||
        e.type == DioExceptionType.sendTimeout) {
      return 'O servidor demorou para responder. Tente novamente.';
    }
    if (e.type == DioExceptionType.connectionError) {
      return 'Sem conexão com o servidor. Verifique sua internet.';
    }

    switch (status) {
      case 400:
        return detail?.toString() ?? 'Dados inválidos. Verifique as informações.';
      case 401:
        return 'Sessão expirada. Faça login novamente.';
      case 403:
        return 'Você não tem permissão para esta ação.';
      case 404:
        return 'Recurso não encontrado.';
      case 409:
        return detail?.toString() ?? 'Conflito: este registro já existe.';
      case 422:
        return 'Dados inválidos enviados ao servidor.';
      case 500:
      case 502:
      case 503:
        return 'Erro no servidor. Tente novamente em instantes.';
      default:
        if (detail != null) return detail.toString();
    }
  }

  final msg = e.toString();
  if (msg.contains('SocketException') || msg.contains('Connection refused')) {
    return 'Sem conexão com o servidor. Verifique sua internet.';
  }
  if (msg.contains('TimeoutException')) {
    return 'Tempo esgotado. Tente novamente.';
  }

  return 'Algo deu errado. Tente novamente.';
}
