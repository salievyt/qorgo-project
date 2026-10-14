import '../../core/design/qorgo_theme.dart';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

class TariffsScreen extends StatefulWidget {
  const TariffsScreen({super.key});
  @override
  State<TariffsScreen> createState() => _TariffsScreenState();
}

class _TariffsScreenState extends State<TariffsScreen> {
  late final Future<Map<String, dynamic>> _catalog;
  bool _annual = false;

  @override
  void initState() {
    super.initState();
    _catalog = rootBundle
        .loadString('assets/tariffs.json')
        .then((source) => jsonDecode(source) as Map<String, dynamic>);
  }

  @override
  Widget build(BuildContext context) => Scaffold(
        appBar: AppBar(title: const Text('Тарифы QORGO')),
        body: FutureBuilder<Map<String, dynamic>>(
          future: _catalog,
          builder: (context, snapshot) {
            if (snapshot.hasError) {
              return const Center(child: Text('Не удалось загрузить тарифы'));
            }
            if (!snapshot.hasData) {
              return const Center(child: CircularProgressIndicator());
            }
            final catalog = snapshot.data!;
            return Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 560),
                child: ListView(
                  padding: const EdgeInsets.all(20),
                  children: [
                    Text('Начните бесплатно',
                        style: Theme.of(context).textTheme.headlineMedium),
                    const SizedBox(height: 12),
                    Text(catalog['notice'] as String),
                    const SizedBox(height: 20),
                    Wrap(spacing: 8, runSpacing: 8, children: [
                      ChoiceChip(
                          label: const Text('Месяц'),
                          selected: !_annual,
                          onSelected: (_) => setState(() => _annual = false)),
                      ChoiceChip(
                          label: const Text('Год · экономия 17%'),
                          selected: _annual,
                          onSelected: (_) => setState(() => _annual = true)),
                    ]),
                    const SizedBox(height: 16),
                    for (final plan in catalog['plans'] as List)
                      _planCard(plan as Map<String, dynamic>),
                    const SizedBox(height: 16),
                    Text(catalog['terms'] as String),
                    const SizedBox(height: 12),
                    const Text(
                        'AI-анализ и история за год — дальнейшие этапы развития. Реакция близких и служб не гарантируется подпиской.'),
                  ],
                ),
              ),
            );
          },
        ),
      );

  Widget _planCard(Map<String, dynamic> plan) {
    final free = plan['id'] == 'free';
    final price = plan[_annual ? 'annual' : 'monthly'] as int;
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(free ? 'Базовый доступ' : 'Планируется',
              style: const TextStyle(color: QorgoDesign.green)),
          const SizedBox(height: 8),
          Text(plan['name'] as String,
              style: Theme.of(context).textTheme.headlineSmall),
          Text(plan['audience'] as String),
          const SizedBox(height: 16),
          Text('$price сом / ${_annual && !free ? 'год' : 'месяц'}',
              style:
                  const TextStyle(fontSize: 28, fontWeight: FontWeight.bold)),
          Text(_annual && !free
              ? '≈ ${(price / 12).round()} сом/месяц · оплата за год целиком'
              : free
                  ? 'Без подписки'
                  : 'При оплате за месяц'),
          if ((plan['features'] as List).isNotEmpty) ...[
            const SizedBox(height: 16),
            const Text('В мобильном MVP',
                style: TextStyle(fontWeight: FontWeight.bold)),
            for (final feature in plan['features'] as List)
              Padding(
                  padding: const EdgeInsets.only(top: 8),
                  child: Text('✓ $feature')),
          ],
          const SizedBox(height: 16),
          const Text('Планируется к запуску',
              style: TextStyle(fontWeight: FontWeight.bold)),
          for (final feature in plan['planned'] as List)
            Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Text('• $feature')),
          const SizedBox(height: 16),
          Text(free
              ? 'Базовые функции доступны в тестовой версии приложения'
              : 'Подключение после запуска платных функций'),
        ]),
      ),
    );
  }
}
