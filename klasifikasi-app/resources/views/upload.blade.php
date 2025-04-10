<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    <title>Upload Gambar</title>
</head>
<body class="p-15 font-medium font-mono">
    <h1 class="text-center font-bold mb-20 text-4xl">Performance Test Classification</h1>
    <div class="shadow-lg rounded-lg bg-blue-100 p-5">
        <h1 class="font-black text-4xl mb-10">Klasifikasi Gambar [FLASK]</h1>
        <form action="/predict" method="POST" enctype="multipart/form-data">
            @csrf
            <input class="p-2 rounded-lg bg-amber-400 hover:cursor-pointer hover:bg-amber-600" type="file" name="image" required>
            <button type="submit" class="p-2 rounded-lg bg-blue-400 hover:cursor-pointer hover:bg-blue-800 hover:text-white">Klasifikasi</button>
        </form>
    </div>

    <div class="shadow-lg rounded-lg bg-green-100 p-5 mt-15">
        <h1 class="font-black text-4xl mb-10 ">Klasifikasi Gambar [DIRECT LARAVEL]</h1>
        <form action="/predict-direct" method="POST" enctype="multipart/form-data">
            @csrf
            <input class="p-2 rounded-lg bg-amber-400 hover:cursor-pointer hover:bg-amber-600" type="file" name="image" required>
            <button type="submit" class="p-2 rounded-lg bg-blue-400 hover:cursor-pointer hover:bg-blue-800 hover:text-white">Klasifikasi</button>
        </form>
    </div>
    
</body>
</html>
