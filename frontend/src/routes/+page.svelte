<section class="mx-auto max-w-6xl px-4 py-16 sm:px-6 sm:py-24">
	<div class="grid items-end gap-12 lg:grid-cols-12 lg:gap-16">
		<!-- Hero — left-aligned editorial -->
		<div class="lg:col-span-7">
			<p class="label mb-4">Swing Analysis</p>
			<h1 class="page-title leading-none">
				Ukur.<br />
				Analisis.<br />
				<span class="text-highlight">Perbaiki.</span>
			</h1>
			<p class="mt-6 max-w-md text-sm leading-relaxed text-muted">
				Alat analisis performa swing golf berbasis pose detection. Upload video, konfigurasi
				club, dan dapatkan metrik terukur beserta rekomendasi perbaikan.
			</p>
			<div class="mt-10 flex flex-wrap gap-3">
				<a href="/analyze" class="btn-primary">Analisis Swing</a>
				<a href="/report" class="btn-secondary">Laporan Terakhir</a>
			</div>
		</div>

		<!-- Stats panel -->
		<div class="lg:col-span-5">
			<div class="card">
				<p class="label mb-6">Yang Diukur</p>
				<div class="space-y-5">
					{#each [
						{ label: 'Swing Tempo', unit: 'ratio' },
						{ label: 'Postur', unit: 'score' },
						{ label: 'Rotasi', unit: 'degrees' },
						{ label: 'Keseimbangan', unit: 'score' }
					] as metric}
						<div class="flex items-baseline justify-between border-b border-border pb-4 last:border-0 last:pb-0">
							<span class="text-xs font-medium uppercase tracking-wider text-muted">
								{metric.label}
							</span>
							<span class="font-display text-sm font-semibold text-disabled">—</span>
						</div>
					{/each}
				</div>
			</div>
		</div>
	</div>
</section>

<section class="divider">
	<div class="mx-auto max-w-6xl px-4 py-16 sm:px-6">
		<p class="label mb-8">Proses</p>
		<div class="grid gap-px border border-border bg-border sm:grid-cols-3">
			{#each [
				{
					step: '01',
					title: 'Rekam',
					desc: 'Video 3–8 detik dari samping. Kamera setinggi pinggang, jarak 2–3 meter.'
				},
				{
					step: '02',
					title: 'Konfigurasi',
					desc: 'Pilih club dan jenis pukulan agar analisis sesuai konteks swing Anda.'
				},
				{
					step: '03',
					title: 'Review',
					desc: 'Lihat skor, metrik detail, dan rekomendasi perbaikan yang dapat ditindaklanjuti.'
				}
			] as item}
				<div class="bg-graphite p-6">
					<p class="font-display text-2xl font-bold text-border">{item.step}</p>
					<h3 class="mt-3 font-display text-sm font-semibold uppercase tracking-wider text-offwhite">
						{item.title}
					</h3>
					<p class="mt-2 text-sm leading-relaxed text-muted">{item.desc}</p>
				</div>
			{/each}
		</div>
	</div>
</section>

<section class="mx-auto max-w-6xl px-4 pb-20 sm:px-6">
	<div class="flex flex-col items-start justify-between gap-6 border border-border bg-graphite p-6 sm:flex-row sm:items-center">
		<div>
			<p class="label">Siap Mulai</p>
			<p class="font-display text-lg font-semibold text-offwhite">
				Baca panduan rekaman sebelum sesi pertama.
			</p>
		</div>
		<a href="/analyze" class="btn-primary shrink-0">Mulai Sesi</a>
	</div>
</section>
