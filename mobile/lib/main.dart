import 'package:flutter/material.dart';
import 'api.dart';

void main() => runApp(const RoboLabApp());

class RoboLabApp extends StatelessWidget {
  const RoboLabApp({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'RoboLab',
    debugShowCheckedModeBanner: false,
    theme: ThemeData(useMaterial3: true, brightness: Brightness.dark),
    home: const HomePage(),
  );
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});
  @override State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final idea = TextEditingController();
  final api = const RoboLabApi(String.fromEnvironment('ROBOLAB_API', defaultValue: 'http://10.0.2.2:8000'));
  String status = 'Checking backend…';
  String output = '';
  bool busy = false;

  @override void initState() { super.initState(); _check(); }
  Future<void> _check() async {
    try { final h = await api.health(); setState(() => status = 'ONLINE · ${h['version'] ?? ''}'); }
    catch (_) { setState(() => status = 'OFFLINE · backend unavailable'); }
  }
  Future<void> _run(String stage) async {
    if (idea.text.trim().isEmpty) return;
    setState(() { busy = true; output = ''; });
    try {
      final result = await api.runStage(stage, idea.text.trim());
      setState(() => output = result.toString());
    } catch (e) { setState(() => output = 'NOT_TESTED / ERROR: $e'); }
    finally { setState(() => busy = false); }
  }

  @override Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('RoboLab'), actions: [Padding(padding: const EdgeInsets.all(16), child: Center(child: Text(status)))]),
    body: ListView(padding: const EdgeInsets.all(20), children: [
      const Text('Engineering Workspace', style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold)),
      const SizedBox(height: 8),
      const Text('One project → requirements → architecture → circuit → code → verification → compile gate.'),
      const SizedBox(height: 20),
      TextField(controller: idea, minLines: 4, maxLines: 8, decoration: const InputDecoration(border: OutlineInputBorder(), hintText: 'Describe what you want to build…')),
      const SizedBox(height: 12),
      Wrap(spacing: 8, runSpacing: 8, children: [
        for (final s in ['architect','component','circuit','code','cad','simulation','verifier_1','verifier_2','compiler_1','compiler_2','consensus'])
          FilledButton.tonal(onPressed: busy ? null : () => _run(s), child: Text(s)),
      ]),
      const SizedBox(height: 20),
      if (busy) const LinearProgressIndicator(),
      if (output.isNotEmpty) SelectableText(output, style: const TextStyle(fontFamily: 'monospace')),
    ]),
  );
}
