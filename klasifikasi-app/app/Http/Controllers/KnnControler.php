<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;

class KnnControler extends Controller
{
    public function predict(Request $request)
    {
        $python = "C:\\Users\\acer\\AppData\\Local\\Programs\\PythonCodingPack\\python.exe";

        // Simpan gambar upload
        $path = $request->file('image')->store('uploads', 'public');
        $imagePath = public_path('storage/' . $path);

        // Path ke Python script
        $script = public_path('predict.py');

        // Jalankan Python
        $command = "\"$python\" \"$script\" \"$imagePath\"";
        $output = shell_exec($command);

        return view('upload', ['result' => $output]);
    }
}

