import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = 'https://ytfwprdrnvgujxdmvvnr.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl0ZndwcmRybnZndWp4ZG12dm5yIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzE3MDkzOTAsImV4cCI6MjA0NzI4NTM5MH0.fwaLYvcufyShNhg0fprZekQr4oeL02VceSVB5FAm0rw';

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
    realtime: {
        enabled:true,
    },
});
