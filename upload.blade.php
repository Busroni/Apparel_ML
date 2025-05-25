<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    <script src="https://code.jquery.com/jquery-3.7.1.js" integrity="sha256-eKhayi8LEQwp4NKxN+CfCh+3qOVUtJn3QNZ0TciWLP4=" crossorigin="anonymous"></script>
    <title>Upload Gambar</title>
</head>
<body class="p-15 font-medium font-mono bg-slate-800">
    <h1 class="text-center text-white font-bold mb-20 text-4xl">Classification Testing Process</h1>
    <div class="shadow-lg rounded-lg bg-blue-100 p-5">
        <h1 class="font-black text-4xl mb-10">Klasifikasi Gambar [FLASK]</h1>
        <form action="/predict" method="POST" enctype="multipart/form-data">
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
                <h2 class="text-xl font-bold mb-2">{{ asset($image) }}</h2>
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

        <div class="shadow-lg rounded-lg bg-blue-100 p-5">
            <h1 class="font-black text-4xl mb-10">Klasifikasi Part</h1>
            <form action="/predict-part" method="POST" enctype="multipart/form-data">
                @csrf
                <input type="hidden" name="image" value="{{ $image }}">
                {{ $image }}
                <button type="submit" class="p-2 rounded-lg bg-blue-400 hover:cursor-pointer hover:bg-blue-800 hover:text-white">Klasifikasi</button>
            </form>
        </div>
    @endif

    
    <!-- Dropdown -->
    <select id="dropdown-opsi"class="text-xl font-bold w-1/2 max-w-md px-4 py-2 rounded bg-amber-100">
        <option value="" selected disabled>Bagaimana kesalahan sistem?</option>
        <option value="modalA">Hasil klasifikasi salah.</option>
        <option value="modalB">Object yang terdeteksi tidak lengkap atau ada yang salah.</option>
        <option value="modalC">Object tidak terdeteksi.</option>
        </select>

<!-- Modal Template -->
<div id="modalA" class="hidden fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
  <div class="bg-white p-6 rounded shadow-lg w-1/3">
    <h2 class="text-xl font-bold mb-4">Modal A</h2>
    <p>Isi konten A di sini.</p>
    <button class="mt-4 bg-blue-500 text-white px-4 py-2 rounded close-modal">Tutup</button>
  </div>
</div>

<div id="modalB" class="hidden fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
  <div class="bg-white p-6 rounded shadow-lg w-1/3">
    <h2 class="text-xl font-bold mb-4">Modal B</h2>
    <p>Isi konten B di sini.</p>
    <button class="mt-4 bg-blue-500 text-white px-4 py-2 rounded close-modal">Tutup</button>
  </div>
</div>

<div id="modalC" class="hidden fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
  <div class="bg-white p-6 rounded shadow-lg w-1/3">
    <h2 class="text-xl font-bold mb-4">Modal C</h2>
    <p>Isi konten C di sini.</p>
    <button class="mt-4 bg-blue-500 text-white px-4 py-2 rounded close-modal">Tutup</button>
  </div>
</div>

<script>
    $('#dropdown-opsi').on('change', function () {
  const selected = $(this).val();

  // Tutup semua modal jika terbuka
  $('.fixed').addClass('hidden');

  // Buka modal sesuai value
    $('#' + selected).removeClass('hidden');
    });

    // Tombol untuk menutup modal
    $('.close-modal').on('click', function () {
    $(this).closest('.fixed').addClass('hidden');
});

</script>

</body>
</html>
