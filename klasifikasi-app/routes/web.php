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

Route::post('/predict-direct', [KnnController::class, 'predictDirect']);
