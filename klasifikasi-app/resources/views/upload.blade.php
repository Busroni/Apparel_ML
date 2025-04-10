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

    @if(isset($type))
        <div class="mt-5 bg-green-200 p-4 rounded-lg">
            <h2 class="text-xl font-bold">Hasil Percobaan {{ $type }}:</h2>

            @if(isset($duration))
            <h2 class="text-lg">lama proses : {{ $duration }} s</h2>
            @endif

            @if(isset($image))
            <div class="mt-10">
                <h2 class="text-xl font-bold mb-2">Gambar yang diupload:</h2>
                <img src="{{ asset($image) }}" alt="Uploaded Image" class="w-64 rounded-lg shadow" />
            </div>
            @endif
        
            @if(isset($result))
                <div class="mt-5 bg-green-200 p-4 rounded-lg">
                    <h2 class="text-xl font-bold">Hasil Klasifikasi:</h2>
                    <p class="text-lg text-gray-700">{{ $result }}</p>
                </div>
            @endif

        </div>
    @endif

    <script>
        window.addEventListener('DOMContentLoaded', function () {
            let startTime = 0;
    
            const form = document.getElementById('direct-form');
            const timeDiv = document.getElementById('response-time');
    
            if (form) {
                form.addEventListener('submit', function () {
                    startTime = performance.now();
                });
            }
    
            if (startTime > 0 && timeDiv) {
                const endTime = performance.now();
                const duration = (endTime - startTime) / 1000;
                timeDiv.textContent = `⏱️ Response Time: ${duration.toFixed(2)} seconds`;
            }
        });
    </script>
    
</body>
</html>
