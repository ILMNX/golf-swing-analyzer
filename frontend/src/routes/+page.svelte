<section class="relative overflow-hidden">
	<!-- Hero background -->
	<div class="absolute inset-0 bg-gradient-to-b from-fairway-900/80 via-fairway-950 to-fairway-950"></div>
	<div
		class="absolute inset-0 opacity-20"
		style="background-image: radial-gradient(circle at 20% 50%, #22c55e 0%, transparent 50%), radial-gradient(circle at 80% 20%, #15803d 0%, transparent 40%);"
	></div>

	<div class="relative mx-auto max-w-6xl px-4 py-20 sm:px-6 sm:py-28">
		<div class="mx-auto max-w-3xl text-center">
			<div
				class="mb-6 inline-flex items-center gap-2 rounded-full border border-fairway-700 bg-fairway-900/60 px-4 py-1.5 text-sm text-fairway-300"
			>
				<span class="h-2 w-2 rounded-full bg-fairway-400"></span>
				Powered by YOLOv8 Pose Detection
			</div>

			<h1 class="font-display text-4xl font-bold leading-tight text-white sm:text-6xl">
				Analisis Swing Golf
				<span class="block text-fairway-400">Lebih Pintar & Akurat</span>
			</h1>

			<p class="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-fairway-300">
				Upload video swing Anda, pilih club yang digunakan, dan dapatkan skor plus rekomendasi
				perbaikan berbasis AI pose estimation dalam hitungan detik.
			</p>

			<div class="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
				<a href="/analyze" class="btn-primary text-base px-8 py-4">
					Mulai Analisis
					<span aria-hidden="true">→</span>
				</a>
				<a href="/report" class="btn-secondary text-base px-8 py-4"> Lihat Laporan Terakhir </a>
			</div>
		</div>
	</div>
</section>

<!-- Features -->
<section class="mx-auto max-w-6xl px-4 py-16 sm:px-6">
	<div class="mb-12 text-center">
		<h2 class="font-display text-3xl font-semibold text-white">Bagaimana Cara Kerjanya?</h2>
		<p class="mt-2 text-fairway-400">Tiga langkah sederhana menuju swing yang lebih baik</p>
	</div>

	<div class="grid gap-6 md:grid-cols-3">
		{#each [
			{
				step: '01',
				title: 'Rekam Swing',
				desc: 'Rekam video swing dari samping dengan pencahayaan yang baik. Durasi 3–8 detik sudah cukup.',
				icon: '🎥'
			},
			{
				step: '02',
				title: 'Konfigurasi Club',
				desc: 'Pilih driver, iron, wedge, atau putter. Sesuaikan jenis pukulan: full swing, chip, pitch, atau putt.',
				icon: '🏌️'
			},
			{
				step: '03',
				title: 'Dapatkan Laporan',
				desc: 'AI menganalisis pose tubuh Anda dan memberikan skor, metrik detail, serta rekomendasi perbaikan.',
				icon: '📊'
			}
		] as feature}
			<div class="card group transition hover:border-fairway-600">
				<div class="mb-4 flex items-center justify-between">
					<span class="text-3xl">{feature.icon}</span>
					<span class="font-display text-4xl font-bold text-fairway-800 group-hover:text-fairway-700">
						{feature.step}
					</span>
				</div>
				<h3 class="text-lg font-semibold text-white">{feature.title}</h3>
				<p class="mt-2 text-sm leading-relaxed text-fairway-400">{feature.desc}</p>
			</div>
		{/each}
	</div>
</section>

<!-- CTA -->
<section class="mx-auto max-w-6xl px-4 pb-20 sm:px-6">
	<div
		class="card relative overflow-hidden border-fairway-600/50 bg-gradient-to-br from-fairway-900 to-fairway-950"
	>
		<div class="absolute -right-10 -top-10 h-40 w-40 rounded-full bg-fairway-700/20 blur-3xl"></div>
		<div class="relative flex flex-col items-center gap-6 text-center md:flex-row md:text-left">
			<div class="flex-1">
				<h2 class="font-display text-2xl font-semibold text-white sm:text-3xl">
					Siap Meningkatkan Swing Anda?
				</h2>
				<p class="mt-2 text-fairway-300">
					Baca panduan singkat sebelum merekam agar hasil analisis maksimal.
				</p>
			</div>
			<a href="/analyze" class="btn-primary shrink-0"> Analisis Sekarang </a>
		</div>
	</div>
</section>
