-- profiles (extends Supabase Auth users)
CREATE TABLE profiles (
  id         UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  username   TEXT NOT NULL UNIQUE,
  avatar_url TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- alter_egos
CREATE TABLE alter_egos (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  image_url   TEXT NOT NULL,
  selfie_url  TEXT NOT NULL,
  universe    TEXT NOT NULL,
  traits      JSONB DEFAULT '{}',
  created_at  TIMESTAMPTZ DEFAULT now()
);

-- likes
CREATE TABLE likes (
  user_id      UUID REFERENCES profiles(id) ON DELETE CASCADE,
  alter_ego_id UUID REFERENCES alter_egos(id) ON DELETE CASCADE,
  created_at   TIMESTAMPTZ DEFAULT now(),
  PRIMARY KEY (user_id, alter_ego_id)
);

-- Generated alter ego images (public — safe to display in feed)
INSERT INTO storage.buckets (id, name, public) VALUES ('alter-egos', 'alter-egos', true);

-- Raw selfies (private — only accessible via signed URLs)
INSERT INTO storage.buckets (id, name, public) VALUES ('selfies', 'selfies', false);
