import { pgTable, uuid, varchar, text, timestamp, integer, jsonb } from "drizzle-orm/pg-core";

export const signalClients = pgTable("signal_clients", {
  id: uuid("id").defaultRandom().primaryKey(),
  slug: varchar("slug", { length: 50 }).notNull().unique(),
  name: varchar("name", { length: 255 }).notNull(),
  domain: varchar("domain", { length: 255 }).notNull(),
  repo: varchar("repo", { length: 255 }).notNull(),
  config: jsonb("config").notNull(),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
});

export const signalContent = pgTable("signal_content", {
  id: uuid("id").defaultRandom().primaryKey(),
  clientId: uuid("client_id").notNull(),
  type: varchar("type", { length: 50 }).notNull(),
  title: varchar("title", { length: 255 }).notNull(),
  slug: varchar("slug", { length: 255 }).notNull(),
  status: varchar("status", { length: 20 }).notNull(),
  filePath: text("file_path").notNull(),
  qualityScore: integer("quality_score"),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).defaultNow().notNull(),
});

export const signalKeywords = pgTable("signal_keywords", {
  id: uuid("id").defaultRandom().primaryKey(),
  clientId: uuid("client_id").notNull(),
  keyword: varchar("keyword", { length: 255 }).notNull(),
  keywordGroup: varchar("keyword_group", { length: 50 }).notNull(),
  priority: integer("priority").default(0).notNull(),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
});

export const signalRankings = pgTable("signal_rankings", {
  id: uuid("id").defaultRandom().primaryKey(),
  clientId: uuid("client_id").notNull(),
  keywordId: uuid("keyword_id").notNull(),
  position: integer("position").notNull(),
  searchEngine: varchar("search_engine", { length: 50 }).default("google").notNull(),
  snapshotAt: timestamp("snapshot_at", { withTimezone: true }).defaultNow().notNull(),
});

export const signalJobs = pgTable("signal_jobs", {
  id: uuid("id").defaultRandom().primaryKey(),
  clientId: uuid("client_id").notNull(),
  jobType: varchar("job_type", { length: 50 }).notNull(),
  status: varchar("status", { length: 20 }).notNull(),
  payload: jsonb("payload").notNull(),
  error: text("error"),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  finishedAt: timestamp("finished_at", { withTimezone: true }),
});
