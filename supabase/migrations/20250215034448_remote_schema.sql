create extension if not exists "vector" with schema "public" version '0.8.0';

create sequence "public"."segments_id_seq";

create sequence "public"."transcriptions_id_seq";

create sequence "public"."videos_id_seq";

create table "public"."segments" (
    "id" integer not null default nextval('segments_id_seq'::regclass),
    "video_id" integer,
    "speaker_id" text,
    "start_time" double precision,
    "end_time" double precision,
    "text" text,
    "display_text" text,
    "title" text,
    "metadata" jsonb,
    "embedding" vector(1536),
    "created_at" timestamp with time zone default CURRENT_TIMESTAMP,
    "updated_at" timestamp with time zone default CURRENT_TIMESTAMP,
    "deleted_at" timestamp with time zone
);


alter table "public"."segments" enable row level security;

create table "public"."transcriptions" (
    "id" integer not null default nextval('transcriptions_id_seq'::regclass),
    "video_id" integer,
    "raw_transcript" jsonb,
    "created_at" timestamp with time zone default CURRENT_TIMESTAMP,
    "updated_at" timestamp with time zone default CURRENT_TIMESTAMP
);


alter table "public"."transcriptions" enable row level security;

create table "public"."videos" (
    "id" integer not null default nextval('videos_id_seq'::regclass),
    "loom_video_id" text not null,
    "title" text,
    "description" text,
    "thumbnail_url" text,
    "created_at" timestamp with time zone default CURRENT_TIMESTAMP,
    "updated_at" timestamp with time zone default CURRENT_TIMESTAMP,
    "status" text default 'pending'::text,
    "duration" integer,
    "to_process" boolean default true
);


alter table "public"."videos" enable row level security;

alter sequence "public"."segments_id_seq" owned by "public"."segments"."id";

alter sequence "public"."transcriptions_id_seq" owned by "public"."transcriptions"."id";

alter sequence "public"."videos_id_seq" owned by "public"."videos"."id";

CREATE INDEX segments_embedding_idx ON public.segments USING ivfflat (embedding vector_cosine_ops) WITH (lists='100');

CREATE UNIQUE INDEX segments_pkey ON public.segments USING btree (id);

CREATE UNIQUE INDEX transcriptions_pkey ON public.transcriptions USING btree (id);

CREATE UNIQUE INDEX videos_loom_video_id_key ON public.videos USING btree (loom_video_id);

CREATE UNIQUE INDEX videos_pkey ON public.videos USING btree (id);

alter table "public"."segments" add constraint "segments_pkey" PRIMARY KEY using index "segments_pkey";

alter table "public"."transcriptions" add constraint "transcriptions_pkey" PRIMARY KEY using index "transcriptions_pkey";

alter table "public"."videos" add constraint "videos_pkey" PRIMARY KEY using index "videos_pkey";

alter table "public"."segments" add constraint "segments_video_id_fkey" FOREIGN KEY (video_id) REFERENCES videos(id) ON DELETE CASCADE not valid;

alter table "public"."segments" validate constraint "segments_video_id_fkey";

alter table "public"."transcriptions" add constraint "transcriptions_video_id_fkey" FOREIGN KEY (video_id) REFERENCES videos(id) ON DELETE CASCADE not valid;

alter table "public"."transcriptions" validate constraint "transcriptions_video_id_fkey";

alter table "public"."videos" add constraint "videos_loom_video_id_key" UNIQUE using index "videos_loom_video_id_key";

set check_function_bodies = off;

CREATE OR REPLACE FUNCTION public.test_vector()
 RETURNS boolean
 LANGUAGE plpgsql
AS $function$
DECLARE
    test_vector vector(1536);
BEGIN
    -- Create a test vector
    test_vector := array_fill(0::float, ARRAY[1536]);
    RETURN TRUE;
EXCEPTION
    WHEN OTHERS THEN
        RETURN FALSE;
END;
$function$
;

grant delete on table "public"."segments" to "anon";

grant insert on table "public"."segments" to "anon";

grant references on table "public"."segments" to "anon";

grant select on table "public"."segments" to "anon";

grant trigger on table "public"."segments" to "anon";

grant truncate on table "public"."segments" to "anon";

grant update on table "public"."segments" to "anon";

grant delete on table "public"."segments" to "authenticated";

grant insert on table "public"."segments" to "authenticated";

grant references on table "public"."segments" to "authenticated";

grant select on table "public"."segments" to "authenticated";

grant trigger on table "public"."segments" to "authenticated";

grant truncate on table "public"."segments" to "authenticated";

grant update on table "public"."segments" to "authenticated";

grant delete on table "public"."segments" to "service_role";

grant insert on table "public"."segments" to "service_role";

grant references on table "public"."segments" to "service_role";

grant select on table "public"."segments" to "service_role";

grant trigger on table "public"."segments" to "service_role";

grant truncate on table "public"."segments" to "service_role";

grant update on table "public"."segments" to "service_role";

grant delete on table "public"."transcriptions" to "anon";

grant insert on table "public"."transcriptions" to "anon";

grant references on table "public"."transcriptions" to "anon";

grant select on table "public"."transcriptions" to "anon";

grant trigger on table "public"."transcriptions" to "anon";

grant truncate on table "public"."transcriptions" to "anon";

grant update on table "public"."transcriptions" to "anon";

grant delete on table "public"."transcriptions" to "authenticated";

grant insert on table "public"."transcriptions" to "authenticated";

grant references on table "public"."transcriptions" to "authenticated";

grant select on table "public"."transcriptions" to "authenticated";

grant trigger on table "public"."transcriptions" to "authenticated";

grant truncate on table "public"."transcriptions" to "authenticated";

grant update on table "public"."transcriptions" to "authenticated";

grant delete on table "public"."transcriptions" to "service_role";

grant insert on table "public"."transcriptions" to "service_role";

grant references on table "public"."transcriptions" to "service_role";

grant select on table "public"."transcriptions" to "service_role";

grant trigger on table "public"."transcriptions" to "service_role";

grant truncate on table "public"."transcriptions" to "service_role";

grant update on table "public"."transcriptions" to "service_role";

grant delete on table "public"."videos" to "anon";

grant insert on table "public"."videos" to "anon";

grant references on table "public"."videos" to "anon";

grant select on table "public"."videos" to "anon";

grant trigger on table "public"."videos" to "anon";

grant truncate on table "public"."videos" to "anon";

grant update on table "public"."videos" to "anon";

grant delete on table "public"."videos" to "authenticated";

grant insert on table "public"."videos" to "authenticated";

grant references on table "public"."videos" to "authenticated";

grant select on table "public"."videos" to "authenticated";

grant trigger on table "public"."videos" to "authenticated";

grant truncate on table "public"."videos" to "authenticated";

grant update on table "public"."videos" to "authenticated";

grant delete on table "public"."videos" to "service_role";

grant insert on table "public"."videos" to "service_role";

grant references on table "public"."videos" to "service_role";

grant select on table "public"."videos" to "service_role";

grant trigger on table "public"."videos" to "service_role";

grant truncate on table "public"."videos" to "service_role";

grant update on table "public"."videos" to "service_role";

create policy "Enable delete access for all users"
on "public"."segments"
as permissive
for delete
to authenticated
using (true);


create policy "Enable insert access for all users"
on "public"."segments"
as permissive
for insert
to authenticated
with check (true);


create policy "Enable read access for all users"
on "public"."segments"
as permissive
for select
to authenticated
using (true);


create policy "Enable update access for all users"
on "public"."segments"
as permissive
for update
to authenticated
using (true)
with check (true);


create policy "Enable delete access for all users"
on "public"."transcriptions"
as permissive
for delete
to authenticated
using (true);


create policy "Enable insert access for all users"
on "public"."transcriptions"
as permissive
for insert
to authenticated
with check (true);


create policy "Enable read access for all users"
on "public"."transcriptions"
as permissive
for select
to authenticated
using (true);


create policy "Enable update access for all users"
on "public"."transcriptions"
as permissive
for update
to authenticated
using (true)
with check (true);


create policy "Enable delete access for all users"
on "public"."videos"
as permissive
for delete
to authenticated
using (true);


create policy "Enable insert access for all users"
on "public"."videos"
as permissive
for insert
to authenticated
with check (true);


create policy "Enable read access for all users"
on "public"."videos"
as permissive
for select
to authenticated
using (true);


create policy "Enable update access for all users"
on "public"."videos"
as permissive
for update
to authenticated
using (true)
with check (true);



