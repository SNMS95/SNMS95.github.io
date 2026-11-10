// Typed loaders for the YAML files in src/data. Edit the YAML, not the components.
import { load } from 'js-yaml';
import profileRaw from '../data/profile.yaml?raw';
import papersRaw from '../data/papers.yaml?raw';
import softwareRaw from '../data/software.yaml?raw';
import talksRaw from '../data/talks.yaml?raw';

export interface LinkItem {
  label: string;
  url: string;
}

export interface Profile {
  name: string;
  location: string;
  role: string;
  intro: string[];
  links: LinkItem[];
}

export interface Paper {
  id: string;
  title: string;
  authors: string;
  venue: string;
  year: number;
  doi: string;
  arxiv: string;
  pdf: string;
  code: string;
  codeNote: string;
  bibtex: string;
}

export interface Project {
  name: string;
  url: string;
  status: string;
  blurb: string;
}

export interface Contribution {
  name: string;
  url: string;
}

export interface Software {
  projects: Project[];
  contributions: Contribution[];
}

export interface Talk {
  name: string;
  full: string;
  years: string;
}

export const profile = load(profileRaw) as Profile;
export const papers = load(papersRaw) as Paper[];
export const software = load(softwareRaw) as Software;
export const talks = load(talksRaw) as Talk[];

export const SITE_URL = 'https://snms95.github.io';
export const REPO_URL = 'https://github.com/SNMS95/SNMS95.github.io';
