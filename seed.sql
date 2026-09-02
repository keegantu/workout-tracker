--
-- PostgreSQL database dump
--



-- Dumped from database version 18.1 (Postgres.app)
-- Dumped by pg_dump version 18.1 (Postgres.app)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: exercises; Type: TABLE DATA; Schema: public; Owner: keegantu
--

COPY public.exercises (id, name) FROM stdin;
1	Bench Press
3	Squat
4	Deadlift
5	Overhead Press
6	Barbell Row
7	Pull-Up
8	Chin-Up
9	Dumbbell Curl
10	Tricep Pushdown
11	Lat Pulldown
12	Leg Press
13	Romanian Deadlift
14	Incline Bench Press
15	Dumbbell Shoulder Press
16	Lateral Raise
17	Leg Curl
18	Leg Extension
19	Calf Raise
20	Face Pull
21	Hip Thrust
\.


--
-- Name: exercises_id_seq; Type: SEQUENCE SET; Schema: public; Owner: keegantu
--

SELECT pg_catalog.setval('public.exercises_id_seq', 21, true);


--
-- PostgreSQL database dump complete
--



