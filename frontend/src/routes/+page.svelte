<section class="relative overflow-hidden border-b border-border">
	<!-- Hero background: golfer figure, right-aligned -->
	<div class="pointer-events-none absolute inset-0" aria-hidden="true">
		<img
			src="/hero/golfer.jpeg"
			alt=""
			class="absolute inset-0 h-full w-full object-cover object-[75%_center] sm:object-right"
			fetchpriority="high"
		/>
		<div
			class="absolute inset-0 bg-gradient-to-r from-obsidian from-35% via-obsidian/90 via-55% to-obsidian/25 to-100% sm:from-40% sm:via-obsidian/75 sm:to-transparent"
		></div>
		<div class="absolute inset-0 bg-gradient-to-t from-obsidian via-transparent to-obsidian/50"></div>
	</div>

	<div class="container-page relative z-10 py-12 sm:py-16 lg:min-h-[32rem] lg:py-24">
		<div class="grid w-full min-w-0 items-end gap-10 lg:grid-cols-12 lg:gap-16">
			<div class="min-w-0 lg:col-span-7">
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
				<div class="mt-8 flex flex-wrap gap-3 sm:mt-10">
					<a href="/analyze" class="btn-primary">Analisis Swing</a>
					<a href="/report" class="btn-secondary">Laporan Terakhir</a>
				</div>
			</div>

			<div class="min-w-0 lg:col-span-5">
				<div class="card border-border/80 bg-graphite/90 backdrop-blur-[2px]">
				<p class="label mb-6">Yang Diukur</p>
				<div class="space-y-5">
					{#each [
						{ label: 'Swing Tempo' },
						{ label: 'Postur' },
						{ label: 'Rotasi' },
						{ label: 'Keseimbangan' }
					] as metric}
						<div class="flex items-baseline justify-between gap-4 border-b border-border pb-4 last:border-0 last:pb-0">
							<span class="text-xs font-medium uppercase tracking-wide text-muted">
								{metric.label}
							</span>
							<span class="shrink-0 font-display text-sm font-semibold text-disabled">—</span>
						</div>
					{/each}
				</div>
				</div>
			</div>
		</div>
	</div>
</section>

<section class="relative overflow-hidden border-t border-border">
	<div class="pointer-events-none absolute inset-0" aria-hidden="true">
		<img
			src="/process/driving-range.jpeg"
			alt=""
			class="absolute inset-0 h-full w-full object-cover object-center"
			loading="lazy"
		/>
		<div class="absolute inset-0 bg-obsidian/35"></div>
		<div class="absolute inset-0 bg-gradient-to-b from-obsidian/50 via-transparent to-obsidian/40"></div>
	</div>

	<div class="container-page relative z-10 py-12 sm:py-16">
		<p class="label mb-6 sm:mb-8">Proses</p>
		<div class="grid w-full min-w-0 gap-px border border-border bg-border sm:grid-cols-3">
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
				<div class="min-w-0 bg-graphite p-5 sm:p-6">
					<p class="font-display text-2xl font-bold text-border">{item.step}</p>
					<h3 class="mt-3 font-display text-sm font-semibold uppercase tracking-wide text-offwhite">
						{item.title}
					</h3>
					<p class="mt-2 text-sm leading-relaxed text-muted">{item.desc}</p>
				</div>
			{/each}
		</div>
	</div>
</section>

<section class="container-page pb-12 sm:pb-20">
	<div class="flex w-full min-w-0 flex-col items-start justify-between gap-5 border border-border bg-graphite p-5 sm:flex-row sm:items-center sm:gap-6 sm:p-6">
		<div class="min-w-0">
			<p class="label">Siap Mulai</p>
			<p class="font-display text-base font-semibold text-offwhite sm:text-lg">
				Baca panduan rekaman sebelum sesi pertama.
			</p>
		</div>
		<a href="/analyze" class="btn-primary w-full shrink-0 sm:w-auto">Mulai Sesi</a>
	</div>
</section>
