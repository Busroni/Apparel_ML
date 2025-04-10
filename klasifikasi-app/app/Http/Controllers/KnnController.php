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
}