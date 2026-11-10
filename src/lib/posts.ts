import { getCollection } from 'astro:content';

// Drafts are left out of the build. Set SHOW_DRAFTS=1 to include them (preview only).
const showDrafts = process.env.SHOW_DRAFTS === '1';

export async function getPublishedPosts() {
  const posts = await getCollection('posts', ({ data }) => showDrafts || !data.draft);
  return posts.sort((a, b) => b.data.date.valueOf() - a.data.date.valueOf());
}

export function formatDate(d: Date): string {
  return d.toISOString().slice(0, 10);
}
