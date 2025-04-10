<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\KnnController;

Route::get('/', function () {
    return view('welcome');
});

Route::get('/form', function () {
    return view('upload');
});

Route::get('/cek-python', function () {
    $output = shell_exec("where python");
    return "<pre>$output</pre>";
});

Route::post('/predict', [KnnController::class, 'predict']);

Route::post('/predict-direct', function (Request $request) {
    $python = "C:\\Users\\acer\\AppData\\Local\\Programs\\PythonCodingPack\\python.exe";

    // Simpan gambar ke storage
    $path = $request->file('image')->store('uploads', 'public');
    $imagePath = public_path('storage/' . $path);

    // File Python dipindahkan ke folder 'python' di root project
    $script = base_path('python/predict.py');

    // Jalankan script
    $command = "\"$python\" \"$script\" \"$imagePath\"";
    $output = shell_exec($command);

    return "<pre>$output</pre>";
});
