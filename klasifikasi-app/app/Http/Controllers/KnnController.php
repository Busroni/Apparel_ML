<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

class KnnController extends Controller
{
    public function predict(Request $request)
    {
        // Simpan file ke public storage
        $start = microtime(true);
        $path = $request->file('image')->store('uploads', 'public');
        $fullImagePath = storage_path('app/public/' . $path);
        $publicPath = 'storage/' . $path;

        // Kirim file ke Flask server
        $response = Http::attach(
            'image',
            file_get_contents($fullImagePath),
            $request->file('image')->getClientOriginalName()
        )->post('http://127.0.0.1:5000/predict');

        $prediction = $response->json()['prediction'] ?? 'Tidak ada hasil';
        $end = microtime(true);
        $durations = round($end - $start, 2);
        return view('upload', [
            'type' => 'dengan FLask',
            'duration' => $durations,
            'image' => $publicPath,
            'result' => $prediction
        ]);
    }


    public function predictDirect(Request $request)
    {
        $start = microtime(true);
        $python = "C:\\Users\\acer\\AppData\\Local\\Programs\\PythonCodingPack\\python.exe";

        // Simpan gambar ke storage/public/uploads
        $path = $request->file('image')->store('uploads', 'public');
        $imagePath = public_path('storage/' . $path);

        // Path ke script Python
        $script = base_path('python/predict.py');

        // Jalankan script Python
        $command = "\"$python\" \"$script\" \"$imagePath\"";
        $output = shell_exec($command);
        $end = microtime(true);
        $durations = round($end - $start, 2);

        return view('upload', [
            'type' => 'secara Direct Laravel',
            'duration' => $durations,
            'image' => 'storage/' . $path,
            'result' => trim($output)
        ]);
    }

    public function predictFlaskMulti(Request $request)
    {
        set_time_limit(360); 
        $python = "C:\\Users\\acer\\AppData\\Local\\Programs\\PythonCodingPack\\python.exe";
        $script = base_path('python/predict.py');

        $results = [];
        $startAll = microtime(true); // waktu mulai total

        foreach ($request->file('image') as $file) {
            $start = microtime(true); // waktu mulai per gambar

            // Simpan file ke storage/public/uploads
            $path = $file->store('uploads', 'public');
            $imagePath = public_path('storage/' . $path);

            // Jalankan Python script
            $command = "\"$python\" \"$script\" \"$imagePath\"";
            $output = shell_exec($command);

            $end = microtime(true); // waktu selesai per gambar
            $duration = round($end - $start, 2); // detik

            $results[] = [
                'image' => 'storage/' . $path,
                'prediction' => trim($output),
                'time' => $duration
            ];
        }

        $endAll = microtime(true);
        $totalTime = round($endAll - $startAll, 2);

        return view('upload', [
            'results' => $results,
            'totalTime' => $totalTime
        ]);
    }

    public function predictDirectMulti(Request $request)
    {
        set_time_limit(360); 
        $python = "C:\\Users\\acer\\AppData\\Local\\Programs\\PythonCodingPack\\python.exe";
        $script = base_path('python/predict.py');

        $results = [];
        $startAll = microtime(true); // waktu mulai total

        foreach ($request->file('image') as $file) {
            $start = microtime(true); // waktu mulai per gambar

            // Simpan file ke storage/public/uploads
            $path = $file->store('uploads', 'public');
            $imagePath = public_path('storage/' . $path);

            // Jalankan Python script
            $command = "\"$python\" \"$script\" \"$imagePath\"";
            $output = shell_exec($command);

            $end = microtime(true); // waktu selesai per gambar
            $duration = round($end - $start, 2); // detik

            $results[] = [
                'image' => 'storage/' . $path,
                'prediction' => trim($output),
                'time' => $duration
            ];
        }

        $endAll = microtime(true);
        $totalTime = round($endAll - $startAll, 2);

        return view('upload', [
            'results' => $results,
            'totalTime' => $totalTime
        ]);
    }

}