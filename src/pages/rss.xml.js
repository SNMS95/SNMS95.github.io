import rss from '@astrojs/rss';
import { getPublishedPosts } from '../lib/posts';
import { profile } from '../lib/data';

export async function GET(context) {
  const posts = await getPublishedPosts();
  return rss({
    title: `${profile.name}: writing`,
    description: 'Short notes on what I am learning.',
    site: context.site,
    items: posts.map((post) => ({
      title: post.data.title,
      pubDate: post.data.date,
      description: post.data.summary,
      link: `/blog/${post.id}/`,
    })),
  });
}
