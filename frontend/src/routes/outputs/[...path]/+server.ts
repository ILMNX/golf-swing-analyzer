import type { RequestHandler } from './$types';

const BACKEND_URL = process.env.BACKEND_URL ?? 'http://127.0.0.1:3000';

export const GET: RequestHandler = async ({ params, request }) => {
	const path = params.path;
	const range = request.headers.get('range');

	const headers = new Headers();
	if (range) headers.set('Range', range);

	const res = await fetch(`${BACKEND_URL}/outputs/${path}`, { headers });
	if (!res.ok && res.status !== 206) {
		return new Response('Video tidak ditemukan', { status: res.status });
	}

	const outHeaders = new Headers();
	outHeaders.set('Content-Type', res.headers.get('Content-Type') ?? 'video/mp4');
	outHeaders.set('Accept-Ranges', res.headers.get('Accept-Ranges') ?? 'bytes');

	const contentLength = res.headers.get('Content-Length');
	if (contentLength) outHeaders.set('Content-Length', contentLength);

	const contentRange = res.headers.get('Content-Range');
	if (contentRange) outHeaders.set('Content-Range', contentRange);

	const lastModified = res.headers.get('Last-Modified');
	if (lastModified) outHeaders.set('Last-Modified', lastModified);

	return new Response(res.body, {
		status: res.status,
		headers: outHeaders
	});
};
