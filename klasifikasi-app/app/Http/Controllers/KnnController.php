<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

class KnnController extends Controller
{
    public function predict(Request $request)
    {
        $response = Http::attach(
            'image',
            file_get_contents($request->file('image')->getRealPath()),
            $request->file('image')->getClientOriginalName()
        )->post('http://127.0.0.1:5000/predict');

        return response()->json([
            'prediction' => $response->json()['prediction']
        ]);
    }
}