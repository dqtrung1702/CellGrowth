--
-- PostgreSQL database dump
--

-- Dumped from database version 14.17 (Ubuntu 14.17-0ubuntu0.22.04.1)
-- Dumped by pg_dump version 14.17 (Ubuntu 14.17-0ubuntu0.22.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: uaa; Type: SCHEMA; Schema: -; Owner: admin
--

CREATE SCHEMA uaa;


ALTER SCHEMA uaa OWNER TO admin;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: access_request_items; Type: TABLE; Schema: uaa; Owner: admin
--

CREATE TABLE uaa.access_request_items (
    id bigint NOT NULL,
    request_id bigint NOT NULL,
    role_id bigint,
    data_permission_id bigint,
    set_id bigint,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE uaa.access_request_items OWNER TO admin;

--
-- Name: access_request_items_id_seq; Type: SEQUENCE; Schema: uaa; Owner: admin
--

CREATE SEQUENCE uaa.access_request_items_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE uaa.access_request_items_id_seq OWNER TO admin;

--
-- Name: access_request_items_id_seq; Type: SEQUENCE OWNED BY; Schema: uaa; Owner: admin
--

ALTER SEQUENCE uaa.access_request_items_id_seq OWNED BY uaa.access_request_items.id;


--
-- Name: access_request_logs; Type: TABLE; Schema: uaa; Owner: admin
--

CREATE TABLE uaa.access_request_logs (
    id bigint NOT NULL,
    request_id bigint NOT NULL,
    actor_id bigint,
    action character varying(30),
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE uaa.access_request_logs OWNER TO admin;

--
-- Name: access_request_logs_id_seq; Type: SEQUENCE; Schema: uaa; Owner: admin
--

CREATE SEQUENCE uaa.access_request_logs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE uaa.access_request_logs_id_seq OWNER TO admin;

--
-- Name: access_request_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: uaa; Owner: admin
--

ALTER SEQUENCE uaa.access_request_logs_id_seq OWNED BY uaa.access_request_logs.id;


--
-- Name: access_requests; Type: TABLE; Schema: uaa; Owner: admin
--

CREATE TABLE uaa.access_requests (
    id bigint NOT NULL,
    requester_id bigint NOT NULL,
    request_type character varying(20) NOT NULL,
    status character varying(20) DEFAULT 'SUBMITTED'::character varying NOT NULL,
    reason text,
    ttl_hours integer,
    approved_by bigint,
    approved_at timestamp with time zone,
    rejected_reason text,
    apply_result_json jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    requester text
);


ALTER TABLE uaa.access_requests OWNER TO admin;

--
-- Name: access_requests_id_seq; Type: SEQUENCE; Schema: uaa; Owner: admin
--

CREATE SEQUENCE uaa.access_requests_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE uaa.access_requests_id_seq OWNER TO admin;

--
-- Name: access_requests_id_seq; Type: SEQUENCE OWNED BY; Schema: uaa; Owner: admin
--

ALTER SEQUENCE uaa.access_requests_id_seq OWNED BY uaa.access_requests.id;


--
-- Name: alembic_version; Type: TABLE; Schema: uaa; Owner: admin
--

CREATE TABLE uaa.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE uaa.alembic_version OWNER TO admin;

--
-- Name: data_permissions; Type: TABLE; Schema: uaa; Owner: admin
--

CREATE TABLE uaa.data_permissions (
    id bigint NOT NULL,
    permission_id bigint NOT NULL,
    set_id bigint NOT NULL,
    last_update_datetime timestamp with time zone DEFAULT now()
);


ALTER TABLE uaa.data_permissions OWNER TO admin;

--
-- Name: data_permissions_id_seq; Type: SEQUENCE; Schema: uaa; Owner: admin
--

CREATE SEQUENCE uaa.data_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE uaa.data_permissions_id_seq OWNER TO admin;

--
-- Name: data_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: uaa; Owner: admin
--

ALTER SEQUENCE uaa.data_permissions_id_seq OWNED BY uaa.data_permissions.id;


--
-- Name: datasets; Type: TABLE; Schema: uaa; Owner: admin
--

CREATE TABLE uaa.datasets (
    id bigint NOT NULL,
    set_id bigint NOT NULL,
    tablename text NOT NULL,
    colname text NOT NULL,
    colval text NOT NULL
);


ALTER TABLE uaa.datasets OWNER TO admin;

--
-- Name: datasets_id_seq; Type: SEQUENCE; Schema: uaa; Owner: admin
--

CREATE SEQUENCE uaa.datasets_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE uaa.datasets_id_seq OWNER TO admin;

--
-- Name: datasets_id_seq; Type: SEQUENCE OWNED BY; Schema: uaa; Owner: admin
--

ALTER SEQUENCE uaa.datasets_id_seq OWNED BY uaa.datasets.id;


--
-- Name: page_permissions; Type: TABLE; Schema: uaa; Owner: admin
--

CREATE TABLE uaa.page_permissions (
    id bigint NOT NULL,
    permission_id bigint NOT NULL,
    page text NOT NULL,
    last_update_datetime timestamp with time zone DEFAULT now()
);


ALTER TABLE uaa.page_permissions OWNER TO admin;

--
-- Name: page_permissions_id_seq; Type: SEQUENCE; Schema: uaa; Owner: admin
--

CREATE SEQUENCE uaa.page_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE uaa.page_permissions_id_seq OWNER TO admin;

--
-- Name: page_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: uaa; Owner: admin
--

ALTER SEQUENCE uaa.page_permissions_id_seq OWNED BY uaa.page_permissions.id;


--
-- Name: permissions; Type: TABLE; Schema: uaa; Owner: admin
--

CREATE TABLE uaa.permissions (
    id bigint NOT NULL,
    code character varying(100) NOT NULL,
    permission_type character varying(50) NOT NULL,
    description character varying(255),
    last_update_username character varying(50),
    last_update_datetime timestamp with time zone DEFAULT now()
);


ALTER TABLE uaa.permissions OWNER TO admin;

--
-- Name: permissions_id_seq; Type: SEQUENCE; Schema: uaa; Owner: admin
--

CREATE SEQUENCE uaa.permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE uaa.permissions_id_seq OWNER TO admin;

--
-- Name: permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: uaa; Owner: admin
--

ALTER SEQUENCE uaa.permissions_id_seq OWNED BY uaa.permissions.id;


--
-- Name: role_permissions; Type: TABLE; Schema: uaa; Owner: admin
--

CREATE TABLE uaa.role_permissions (
    id bigint NOT NULL,
    role_id bigint NOT NULL,
    permission_id bigint NOT NULL,
    description character varying(255),
    last_update_username character varying(50),
    last_update_datetime timestamp with time zone DEFAULT now()
);


ALTER TABLE uaa.role_permissions OWNER TO admin;

--
-- Name: role_permissions_id_seq; Type: SEQUENCE; Schema: uaa; Owner: admin
--

CREATE SEQUENCE uaa.role_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE uaa.role_permissions_id_seq OWNER TO admin;

--
-- Name: role_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: uaa; Owner: admin
--

ALTER SEQUENCE uaa.role_permissions_id_seq OWNED BY uaa.role_permissions.id;


--
-- Name: roles; Type: TABLE; Schema: uaa; Owner: admin
--

CREATE TABLE uaa.roles (
    id bigint NOT NULL,
    code character varying(100) NOT NULL,
    description character varying(255),
    last_update_username character varying(50),
    last_update_datetime timestamp with time zone DEFAULT now()
);


ALTER TABLE uaa.roles OWNER TO admin;

--
-- Name: roles_id_seq; Type: SEQUENCE; Schema: uaa; Owner: admin
--

CREATE SEQUENCE uaa.roles_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE uaa.roles_id_seq OWNER TO admin;

--
-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: uaa; Owner: admin
--

ALTER SEQUENCE uaa.roles_id_seq OWNED BY uaa.roles.id;


--
-- Name: sets; Type: TABLE; Schema: uaa; Owner: admin
--

CREATE TABLE uaa.sets (
    id bigint NOT NULL,
    setname text NOT NULL,
    services text NOT NULL,
    setcode text NOT NULL
);


ALTER TABLE uaa.sets OWNER TO admin;

--
-- Name: sets_id_seq; Type: SEQUENCE; Schema: uaa; Owner: admin
--

CREATE SEQUENCE uaa.sets_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE uaa.sets_id_seq OWNER TO admin;

--
-- Name: sets_id_seq; Type: SEQUENCE OWNED BY; Schema: uaa; Owner: admin
--

ALTER SEQUENCE uaa.sets_id_seq OWNED BY uaa.sets.id;


--
-- Name: social_providers; Type: TABLE; Schema: uaa; Owner: admin
--

CREATE TABLE uaa.social_providers (
    id integer NOT NULL,
    provider character varying(32) NOT NULL,
    client_id character varying NOT NULL,
    client_secret_enc character varying NOT NULL,
    redirect_uri character varying NOT NULL,
    scopes character varying,
    enabled boolean DEFAULT true NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_by character varying(64)
);


ALTER TABLE uaa.social_providers OWNER TO admin;

--
-- Name: social_providers_id_seq; Type: SEQUENCE; Schema: uaa; Owner: admin
--

CREATE SEQUENCE uaa.social_providers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE uaa.social_providers_id_seq OWNER TO admin;

--
-- Name: social_providers_id_seq; Type: SEQUENCE OWNED BY; Schema: uaa; Owner: admin
--

ALTER SEQUENCE uaa.social_providers_id_seq OWNED BY uaa.social_providers.id;


--
-- Name: url_permissions; Type: TABLE; Schema: uaa; Owner: admin
--

CREATE TABLE uaa.url_permissions (
    id bigint NOT NULL,
    permission_id bigint NOT NULL,
    url text NOT NULL,
    method character varying(10) DEFAULT 'GET'::character varying,
    type character varying(20) DEFAULT 'ROLE'::character varying,
    last_update_datetime timestamp with time zone DEFAULT now()
);


ALTER TABLE uaa.url_permissions OWNER TO admin;

--
-- Name: url_permissions_id_seq; Type: SEQUENCE; Schema: uaa; Owner: admin
--

CREATE SEQUENCE uaa.url_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE uaa.url_permissions_id_seq OWNER TO admin;

--
-- Name: url_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: uaa; Owner: admin
--

ALTER SEQUENCE uaa.url_permissions_id_seq OWNED BY uaa.url_permissions.id;


--
-- Name: user_roles; Type: TABLE; Schema: uaa; Owner: admin
--

CREATE TABLE uaa.user_roles (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    role_id bigint NOT NULL,
    description character varying(255),
    last_update_username character varying(50),
    last_update_datetime timestamp with time zone DEFAULT now()
);


ALTER TABLE uaa.user_roles OWNER TO admin;

--
-- Name: user_roles_id_seq; Type: SEQUENCE; Schema: uaa; Owner: admin
--

CREATE SEQUENCE uaa.user_roles_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE uaa.user_roles_id_seq OWNER TO admin;

--
-- Name: user_roles_id_seq; Type: SEQUENCE OWNED BY; Schema: uaa; Owner: admin
--

ALTER SEQUENCE uaa.user_roles_id_seq OWNED BY uaa.user_roles.id;


--
-- Name: user_totp; Type: TABLE; Schema: uaa; Owner: admin
--

CREATE TABLE uaa.user_totp (
    user_id bigint NOT NULL,
    secret_base32 character varying(64) NOT NULL,
    confirmed boolean DEFAULT false NOT NULL,
    backup_codes_json text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE uaa.user_totp OWNER TO admin;

--
-- Name: users; Type: TABLE; Schema: uaa; Owner: admin
--

CREATE TABLE uaa.users (
    id bigint NOT NULL,
    username character varying(100) NOT NULL,
    password bytea NOT NULL,
    userlocked boolean DEFAULT false NOT NULL,
    name_display character varying(100),
    data_permission_id integer,
    last_signon_datetime timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE uaa.users OWNER TO admin;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: uaa; Owner: admin
--

CREATE SEQUENCE uaa.users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE uaa.users_id_seq OWNER TO admin;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: uaa; Owner: admin
--

ALTER SEQUENCE uaa.users_id_seq OWNED BY uaa.users.id;


--
-- Name: access_request_items id; Type: DEFAULT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.access_request_items ALTER COLUMN id SET DEFAULT nextval('uaa.access_request_items_id_seq'::regclass);


--
-- Name: access_request_logs id; Type: DEFAULT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.access_request_logs ALTER COLUMN id SET DEFAULT nextval('uaa.access_request_logs_id_seq'::regclass);


--
-- Name: access_requests id; Type: DEFAULT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.access_requests ALTER COLUMN id SET DEFAULT nextval('uaa.access_requests_id_seq'::regclass);


--
-- Name: data_permissions id; Type: DEFAULT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.data_permissions ALTER COLUMN id SET DEFAULT nextval('uaa.data_permissions_id_seq'::regclass);


--
-- Name: datasets id; Type: DEFAULT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.datasets ALTER COLUMN id SET DEFAULT nextval('uaa.datasets_id_seq'::regclass);


--
-- Name: page_permissions id; Type: DEFAULT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.page_permissions ALTER COLUMN id SET DEFAULT nextval('uaa.page_permissions_id_seq'::regclass);


--
-- Name: permissions id; Type: DEFAULT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.permissions ALTER COLUMN id SET DEFAULT nextval('uaa.permissions_id_seq'::regclass);


--
-- Name: role_permissions id; Type: DEFAULT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.role_permissions ALTER COLUMN id SET DEFAULT nextval('uaa.role_permissions_id_seq'::regclass);


--
-- Name: roles id; Type: DEFAULT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.roles ALTER COLUMN id SET DEFAULT nextval('uaa.roles_id_seq'::regclass);


--
-- Name: sets id; Type: DEFAULT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.sets ALTER COLUMN id SET DEFAULT nextval('uaa.sets_id_seq'::regclass);


--
-- Name: social_providers id; Type: DEFAULT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.social_providers ALTER COLUMN id SET DEFAULT nextval('uaa.social_providers_id_seq'::regclass);


--
-- Name: url_permissions id; Type: DEFAULT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.url_permissions ALTER COLUMN id SET DEFAULT nextval('uaa.url_permissions_id_seq'::regclass);


--
-- Name: user_roles id; Type: DEFAULT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.user_roles ALTER COLUMN id SET DEFAULT nextval('uaa.user_roles_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.users ALTER COLUMN id SET DEFAULT nextval('uaa.users_id_seq'::regclass);


--
-- Data for Name: access_request_items; Type: TABLE DATA; Schema: uaa; Owner: admin
--

COPY uaa.access_request_items (id, request_id, role_id, data_permission_id, set_id, note, created_at) FROM stdin;
3	2	1	\N	\N	\N	2026-03-14 11:04:03.432998+07
4	2	2	\N	\N	\N	2026-03-14 11:04:03.432998+07
5	2	3	\N	\N	\N	2026-03-14 11:04:03.432998+07
6	2	\N	5	\N	\N	2026-03-14 11:04:03.432998+07
7	2	\N	6	\N	\N	2026-03-14 11:04:03.432998+07
14	1	1	\N	\N	\N	2026-03-22 20:40:09.192089+07
15	1	2	\N	\N	\N	2026-03-22 20:40:09.192089+07
16	1	\N	5	\N	\N	2026-03-22 20:40:09.192089+07
17	3	2	\N	\N	\N	2026-03-27 14:00:16.860973+07
18	3	1	\N	\N	\N	2026-03-27 14:00:16.861084+07
19	3	\N	5	\N	\N	2026-03-27 14:00:16.861119+07
20	3	\N	6	\N	\N	2026-03-27 14:00:16.861148+07
28	4	2	\N	\N	\N	2026-03-27 14:10:12.928661+07
29	4	\N	6	\N	\N	2026-03-27 14:10:12.928759+07
\.


--
-- Data for Name: access_request_logs; Type: TABLE DATA; Schema: uaa; Owner: admin
--

COPY uaa.access_request_logs (id, request_id, actor_id, action, note, created_at) FROM stdin;
1	1	4	SUBMIT	\N	2026-03-14 10:49:53.116466+07
2	2	5	SUBMIT	\N	2026-03-14 11:04:03.432998+07
3	1	4	UPDATE	linh tinh	2026-03-22 13:38:41.688813+07
4	1	4	UPDATE		2026-03-22 13:40:01.069693+07
5	1	4	UPDATE		2026-03-22 13:40:09.195163+07
6	1	4	CANCEL	\N	2026-03-22 13:41:16.605228+07
7	2	1	APPROVE		2026-03-22 13:43:16.508057+07
8	3	3	SUBMIT		2026-03-27 14:00:16.871834+07
9	4	4	SUBMIT		2026-03-27 14:09:44.080461+07
10	4	4	UPDATE		2026-03-27 14:09:57.098594+07
11	4	4	UPDATE		2026-03-27 14:10:12.931832+07
\.


--
-- Data for Name: access_requests; Type: TABLE DATA; Schema: uaa; Owner: admin
--

COPY uaa.access_requests (id, requester_id, request_type, status, reason, ttl_hours, approved_by, approved_at, rejected_reason, apply_result_json, created_at, updated_at, requester) FROM stdin;
1	4	DATA	CANCELLED		\N	\N	\N	\N	\N	2026-03-14 10:49:53.116466+07	2026-03-22 13:41:16.604687+07	trung1
2	5	DATA	APPROVED	\N	\N	1	2026-03-22 13:43:16.506566+07	\N	[{"action": "added", "role_id": 1}, {"action": "added", "role_id": 2}, {"action": "added", "role_id": 3}, {"action": "set", "data_permission_id": 5}]	2026-03-14 11:04:03.432998+07	2026-03-22 13:43:16.506567+07	trung2
3	3	ROLE	SUBMITTED		\N	\N	\N	\N	\N	2026-03-27 14:00:16.842928+07	2026-03-27 14:00:16.842931+07	trung
4	4	ROLE	SUBMITTED		\N	\N	\N	\N	\N	2026-03-27 14:09:44.05997+07	2026-03-27 14:10:12.914641+07	trung1
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: uaa; Owner: admin
--

COPY uaa.alembic_version (version_num) FROM stdin;
3d3b4d67c1a2
\.


--
-- Data for Name: data_permissions; Type: TABLE DATA; Schema: uaa; Owner: admin
--

COPY uaa.data_permissions (id, permission_id, set_id, last_update_datetime) FROM stdin;
1	5	1	2026-03-13 23:23:14.373417+07
2	6	2	2026-03-13 23:23:14.373417+07
\.


--
-- Data for Name: datasets; Type: TABLE DATA; Schema: uaa; Owner: admin
--

COPY uaa.datasets (id, set_id, tablename, colname, colval) FROM stdin;
6	3	PERSON	CODE	*
26	1	*	*	*
39	2	SETS	SETCODE	*
40	2	PERMISSIONS	CODE	*
41	2	ROLES	CODE	PERSON
42	2	ROLES	CODE	UAA
43	2	USERS	USERNAME	*
44	2	ACCESS_REQUESTS	STATUS	SUBMITTED
\.


--
-- Data for Name: page_permissions; Type: TABLE DATA; Schema: uaa; Owner: admin
--

COPY uaa.page_permissions (id, permission_id, page, last_update_datetime) FROM stdin;
14	3	/home	2026-03-31 20:29:26.220187+07
15	3	/Role	2026-03-31 20:29:26.220187+07
16	3	/Permission	2026-03-31 20:29:26.220187+07
17	3	/User	2026-03-31 20:29:26.220187+07
18	3	/datasets	2026-03-31 20:29:26.220187+07
19	3	/access_requests	2026-03-31 20:29:26.220187+07
32	3	/mfa/totp/setup	2026-03-31 21:33:16.491237+07
40	4	/home	2026-03-31 14:49:32.187825+07
41	4	/Permission	2026-03-31 14:49:32.18785+07
42	4	/User	2026-03-31 14:49:32.187869+07
43	4	/datasets	2026-03-31 14:49:32.187887+07
44	4	/access_requests	2026-03-31 14:49:32.187905+07
\.


--
-- Data for Name: permissions; Type: TABLE DATA; Schema: uaa; Owner: admin
--

COPY uaa.permissions (id, code, permission_type, description, last_update_username, last_update_datetime) FROM stdin;
5	FULL_DATA	DATA	Full data access	\N	2026-03-13 23:23:14.360633+07
6	UAA_DATA	DATA	Scope for UAA user	\N	2026-03-13 23:23:14.360633+07
3	ALL_ROLE	ROLE	Full access via cookie	\N	2026-03-31 13:26:27.897142+07
4	UAA	ROLE	uaa access	\N	2026-03-31 14:49:32.181171+07
\.


--
-- Data for Name: role_permissions; Type: TABLE DATA; Schema: uaa; Owner: admin
--

COPY uaa.role_permissions (id, role_id, permission_id, description, last_update_username, last_update_datetime) FROM stdin;
1	1	3	\N	\N	2026-03-13 23:23:14.373417+07
2	2	4	\N	\N	2026-03-13 23:23:14.373417+07
\.


--
-- Data for Name: roles; Type: TABLE DATA; Schema: uaa; Owner: admin
--

COPY uaa.roles (id, code, description, last_update_username, last_update_datetime) FROM stdin;
1	Admin	Administrator	\N	2026-03-13 23:23:14.358326+07
2	UAA	UAA	\N	2026-03-13 23:23:14.358326+07
3	PERSON	PERSON	\N	2026-03-13 23:23:14.358326+07
\.


--
-- Data for Name: sets; Type: TABLE DATA; Schema: uaa; Owner: admin
--

COPY uaa.sets (id, setname, services, setcode) FROM stdin;
2	UAA	UAA	UAA
3	PERSON	PERSON	PERSON
1	ALL	*	*
\.


--
-- Data for Name: social_providers; Type: TABLE DATA; Schema: uaa; Owner: admin
--

COPY uaa.social_providers (id, provider, client_id, client_secret_enc, redirect_uri, scopes, enabled, updated_at, updated_by) FROM stdin;
1	google	629811820083-u4amf8fnogu9a1thu71ef8201mv71bk3.apps.googleusercontent.com	QoC7WRfmN87Ge0X9g8_T2RhoEG_j5PbT2y-eY4e1HzV0u5w=	http://localhost:8082/auth/google/callback	openid email profile	t	2026-03-30 14:01:14.970801	seed_script
\.


--
-- Data for Name: url_permissions; Type: TABLE DATA; Schema: uaa; Owner: admin
--

COPY uaa.url_permissions (id, permission_id, url, method, type, last_update_datetime) FROM stdin;
81	3	/login	POST	ROLE	2026-03-31 20:30:54.1826+07
82	3	/register	POST	ROLE	2026-03-31 20:30:54.1826+07
83	3	/check_auth_ext	POST	ROLE	2026-03-31 20:30:54.1826+07
84	3	/getUserList	POST	ROLE	2026-03-31 20:30:54.1826+07
85	3	/getUserInfo	POST	ROLE	2026-03-31 20:30:54.1826+07
86	3	/updateUser	POST	ROLE	2026-03-31 20:30:54.1826+07
87	3	/updateUserRole	POST	ROLE	2026-03-31 20:30:54.1826+07
88	3	/getRoleList	POST	ROLE	2026-03-31 20:30:54.1826+07
89	3	/getRoleInfo	POST	ROLE	2026-03-31 20:30:54.1826+07
90	3	/addRole	POST	ROLE	2026-03-31 20:30:54.1826+07
91	3	/updateRole	POST	ROLE	2026-03-31 20:30:54.1826+07
92	3	/deleteRoleById	POST	ROLE	2026-03-31 20:30:54.1826+07
93	3	/getPermissionByRole	POST	ROLE	2026-03-31 20:30:54.1826+07
94	3	/getUserByRole	POST	ROLE	2026-03-31 20:30:54.1826+07
95	3	/getRoleByUser	POST	ROLE	2026-03-31 20:30:54.1826+07
96	3	/getPermissionList	POST	ROLE	2026-03-31 20:30:54.1826+07
97	3	/getPermissionInfo	POST	ROLE	2026-03-31 20:30:54.1826+07
98	3	/addPermission	POST	ROLE	2026-03-31 20:30:54.1826+07
99	3	/updatePermission	POST	ROLE	2026-03-31 20:30:54.1826+07
100	3	/deletePermissionById	POST	ROLE	2026-03-31 20:30:54.1826+07
101	3	/getURLbyPermission	POST	ROLE	2026-03-31 20:30:54.1826+07
102	3	/getURLbyPermissionList	POST	ROLE	2026-03-31 20:30:54.1826+07
103	3	/getRoleByPermission	POST	ROLE	2026-03-31 20:30:54.1826+07
104	3	/getDataPermissionList	POST	ROLE	2026-03-31 20:30:54.1826+07
105	3	/getRolePermissionList	POST	ROLE	2026-03-31 20:30:54.1826+07
106	3	/getDataSetByUser	POST	ROLE	2026-03-31 20:30:54.1826+07
107	3	/getSetList	POST	ROLE	2026-03-31 20:30:54.1826+07
108	3	/addSet	POST	ROLE	2026-03-31 20:30:54.1826+07
109	3	/updateSet	POST	ROLE	2026-03-31 20:30:54.1826+07
110	3	/deleteSetById	POST	ROLE	2026-03-31 20:30:54.1826+07
111	3	/getDatasetBySet	POST	ROLE	2026-03-31 20:30:54.1826+07
112	3	/updateDatasetBySet	POST	ROLE	2026-03-31 20:30:54.1826+07
113	3	/getPageByUser	POST	ROLE	2026-03-31 20:30:54.1826+07
114	3	/getDatasetByPermission	POST	ROLE	2026-03-31 20:30:54.1826+07
115	3	/access_requests	POST	ROLE	2026-03-31 20:30:54.1826+07
116	3	/access_requests	GET	ROLE	2026-03-31 20:30:54.1826+07
117	3	/access_requests/%	GET	ROLE	2026-03-31 20:30:54.1826+07
118	3	/access_requests/%/approve	POST	ROLE	2026-03-31 20:30:54.1826+07
119	3	/access_requests/%/reject	POST	ROLE	2026-03-31 20:30:54.1826+07
120	3	/access_requests/%/cancel	POST	ROLE	2026-03-31 20:30:54.1826+07
180	3	/mfa/totp/enroll	POST	ROLE	2026-03-31 21:33:16.485839+07
182	3	/mfa/totp/verify	POST	ROLE	2026-03-31 21:33:16.485839+07
184	3	/mfa/totp/verify_login	POST	ROLE	2026-03-31 21:33:16.485839+07
186	3	/mfa/totp/disable	POST	ROLE	2026-03-31 21:33:16.485839+07
232	4	/login	POST	ROLE	2026-03-31 14:49:32.186607+07
233	4	/register	POST	ROLE	2026-03-31 14:49:32.186798+07
234	4	/check_auth_ext	POST	ROLE	2026-03-31 14:49:32.186838+07
235	4	/getUserList	POST	ROLE	2026-03-31 14:49:32.186866+07
236	4	/getUserInfo	POST	ROLE	2026-03-31 14:49:32.186899+07
237	4	/updateUser	POST	ROLE	2026-03-31 14:49:32.186924+07
238	4	/updateUserRole	POST	ROLE	2026-03-31 14:49:32.186946+07
239	4	/getRoleList	POST	ROLE	2026-03-31 14:49:32.186969+07
240	4	/getRoleInfo	POST	ROLE	2026-03-31 14:49:32.186991+07
241	4	/addRole	POST	ROLE	2026-03-31 14:49:32.187012+07
242	4	/updateRole	POST	ROLE	2026-03-31 14:49:32.187035+07
243	4	/deleteRoleById	POST	ROLE	2026-03-31 14:49:32.187058+07
244	4	/getPermissionByRole	POST	ROLE	2026-03-31 14:49:32.187079+07
245	4	/getUserByRole	POST	ROLE	2026-03-31 14:49:32.187101+07
246	4	/getRoleByUser	POST	ROLE	2026-03-31 14:49:32.187122+07
247	4	/getPermissionList	POST	ROLE	2026-03-31 14:49:32.187143+07
248	4	/getPermissionInfo	POST	ROLE	2026-03-31 14:49:32.187167+07
249	4	/addPermission	POST	ROLE	2026-03-31 14:49:32.187189+07
250	4	/updatePermission	POST	ROLE	2026-03-31 14:49:32.187211+07
251	4	/deletePermissionById	POST	ROLE	2026-03-31 14:49:32.187233+07
252	4	/getURLbyPermission	POST	ROLE	2026-03-31 14:49:32.187281+07
253	4	/getURLbyPermissionList	POST	ROLE	2026-03-31 14:49:32.187314+07
254	4	/getRoleByPermission	POST	ROLE	2026-03-31 14:49:32.18734+07
255	4	/getDataPermissionList	POST	ROLE	2026-03-31 14:49:32.187364+07
256	4	/getRolePermissionList	POST	ROLE	2026-03-31 14:49:32.187387+07
257	4	/getDataSetByUser	POST	ROLE	2026-03-31 14:49:32.187409+07
258	4	/getSetList	POST	ROLE	2026-03-31 14:49:32.187432+07
259	4	/addSet	POST	ROLE	2026-03-31 14:49:32.187455+07
260	4	/updateSet	POST	ROLE	2026-03-31 14:49:32.187477+07
261	4	/deleteSetById	POST	ROLE	2026-03-31 14:49:32.187499+07
262	4	/getDatasetBySet	POST	ROLE	2026-03-31 14:49:32.187521+07
263	4	/updateDatasetBySet	POST	ROLE	2026-03-31 14:49:32.187543+07
264	4	/getPageByUser	POST	ROLE	2026-03-31 14:49:32.187565+07
265	4	/getDatasetByPermission	POST	ROLE	2026-03-31 14:49:32.187587+07
266	4	/access_requests	POST	ROLE	2026-03-31 14:49:32.187608+07
267	4	/access_requests	GET	ROLE	2026-03-31 14:49:32.18763+07
268	4	/access_requests/%	GET	ROLE	2026-03-31 14:49:32.187651+07
269	4	/access_requests/%/approve	POST	ROLE	2026-03-31 14:49:32.187673+07
270	4	/access_requests/%/reject	POST	ROLE	2026-03-31 14:49:32.187695+07
271	4	/access_requests/%/cancel	POST	ROLE	2026-03-31 14:49:32.187716+07
272	4	/mfa/totp/enroll	POST	ROLE	2026-03-31 14:49:32.187737+07
273	4	/mfa/totp/verify	POST	ROLE	2026-03-31 14:49:32.187758+07
274	4	/mfa/totp/verify_login	POST	ROLE	2026-03-31 14:49:32.18778+07
275	4	/mfa/totp/disable	POST	ROLE	2026-03-31 14:49:32.187803+07
\.


--
-- Data for Name: user_roles; Type: TABLE DATA; Schema: uaa; Owner: admin
--

COPY uaa.user_roles (id, user_id, role_id, description, last_update_username, last_update_datetime) FROM stdin;
1	1	1	\N	\N	2026-03-13 23:23:14.373417+07
2	2	2	\N	\N	2026-03-13 23:23:14.373417+07
3	5	1	\N	\N	2026-03-22 13:43:16.499087+07
4	5	2	\N	\N	2026-03-22 13:43:16.502731+07
5	5	3	\N	\N	2026-03-22 13:43:16.503141+07
\.


--
-- Data for Name: user_totp; Type: TABLE DATA; Schema: uaa; Owner: admin
--

COPY uaa.user_totp (user_id, secret_base32, confirmed, backup_codes_json, created_at, updated_at) FROM stdin;
1	GW6JUIVEPO2QBGJY5HCASXPGY5EJ4MOR	t	\N	2026-03-31 14:34:18.456145+07	2026-03-31 14:34:18.456147+07
2	O6S475I7SH4X3O2BRLWJMZKO6ZQINY5W	f	\N	2026-03-31 14:46:08.747192+07	2026-03-31 14:46:08.747196+07
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: uaa; Owner: admin
--

COPY uaa.users (id, username, password, userlocked, name_display, data_permission_id, last_signon_datetime, created_at, updated_at) FROM stdin;
2	uaa	\\x243261243132246e6d7376536f5468495563412f657033415a6454324f546263517130624556385233654d4e494c37734e4f342e2e55493473717165	f	\N	6	2026-03-31 14:59:11.523278+07	2026-03-13 23:23:13.685218+07	2026-03-13 23:23:13.685218+07
3	trung	\\x24326124313224414a634a6f6d7a4e384e56414f7247757142545a4a6566644545446e4c795079702e547863512f456b577a52547349466b32555332	f	\N	\N	2026-03-27 13:49:44.528478+07	2026-03-13 23:23:13.685218+07	2026-03-13 23:23:13.685218+07
4	trung1	\\x2432622431322439733168706d5731687755574c69316b4f53674d732e434a7a34324a376d4554745a756d3067576c4d4b544c5765514c6c5437384f	f	trung1	\N	2026-03-27 14:08:59.418664+07	2026-03-14 10:49:53.111658+07	2026-03-14 10:49:53.111658+07
5	trung2	\\x243262243132244855474f3342797537503163705054376d7479754e2e776550575731487949643042596e6f72616245307945303374533150503765	f		5	2026-03-22 13:42:10.328961+07	2026-03-14 11:04:03.429838+07	2026-03-22 13:43:16.50499+07
1	admin	\\x2432612431322435584779644374506f39745241425248446b66485875746d4e6164786954674638716e4b626b642f4679394d71746942495239512e	f	\N	5	2026-03-31 14:40:40.954486+07	2026-03-13 23:23:13.685218+07	2026-03-13 23:23:13.685218+07
\.


--
-- Name: access_request_items_id_seq; Type: SEQUENCE SET; Schema: uaa; Owner: admin
--

SELECT pg_catalog.setval('uaa.access_request_items_id_seq', 29, true);


--
-- Name: access_request_logs_id_seq; Type: SEQUENCE SET; Schema: uaa; Owner: admin
--

SELECT pg_catalog.setval('uaa.access_request_logs_id_seq', 11, true);


--
-- Name: access_requests_id_seq; Type: SEQUENCE SET; Schema: uaa; Owner: admin
--

SELECT pg_catalog.setval('uaa.access_requests_id_seq', 4, true);


--
-- Name: data_permissions_id_seq; Type: SEQUENCE SET; Schema: uaa; Owner: admin
--

SELECT pg_catalog.setval('uaa.data_permissions_id_seq', 2, true);


--
-- Name: datasets_id_seq; Type: SEQUENCE SET; Schema: uaa; Owner: admin
--

SELECT pg_catalog.setval('uaa.datasets_id_seq', 44, true);


--
-- Name: page_permissions_id_seq; Type: SEQUENCE SET; Schema: uaa; Owner: admin
--

SELECT pg_catalog.setval('uaa.page_permissions_id_seq', 44, true);


--
-- Name: permissions_id_seq; Type: SEQUENCE SET; Schema: uaa; Owner: admin
--

SELECT pg_catalog.setval('uaa.permissions_id_seq', 1, false);


--
-- Name: role_permissions_id_seq; Type: SEQUENCE SET; Schema: uaa; Owner: admin
--

SELECT pg_catalog.setval('uaa.role_permissions_id_seq', 2, true);


--
-- Name: roles_id_seq; Type: SEQUENCE SET; Schema: uaa; Owner: admin
--

SELECT pg_catalog.setval('uaa.roles_id_seq', 3, true);


--
-- Name: sets_id_seq; Type: SEQUENCE SET; Schema: uaa; Owner: admin
--

SELECT pg_catalog.setval('uaa.sets_id_seq', 4, true);


--
-- Name: social_providers_id_seq; Type: SEQUENCE SET; Schema: uaa; Owner: admin
--

SELECT pg_catalog.setval('uaa.social_providers_id_seq', 1, true);


--
-- Name: url_permissions_id_seq; Type: SEQUENCE SET; Schema: uaa; Owner: admin
--

SELECT pg_catalog.setval('uaa.url_permissions_id_seq', 275, true);


--
-- Name: user_roles_id_seq; Type: SEQUENCE SET; Schema: uaa; Owner: admin
--

SELECT pg_catalog.setval('uaa.user_roles_id_seq', 5, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: uaa; Owner: admin
--

SELECT pg_catalog.setval('uaa.users_id_seq', 5, true);


--
-- Name: access_request_items access_request_items_pkey; Type: CONSTRAINT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.access_request_items
    ADD CONSTRAINT access_request_items_pkey PRIMARY KEY (id);


--
-- Name: access_request_items access_request_items_request_id_role_id_data_permission_id__key; Type: CONSTRAINT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.access_request_items
    ADD CONSTRAINT access_request_items_request_id_role_id_data_permission_id__key UNIQUE (request_id, role_id, data_permission_id, set_id);


--
-- Name: access_request_logs access_request_logs_pkey; Type: CONSTRAINT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.access_request_logs
    ADD CONSTRAINT access_request_logs_pkey PRIMARY KEY (id);


--
-- Name: access_requests access_requests_pkey; Type: CONSTRAINT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.access_requests
    ADD CONSTRAINT access_requests_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: data_permissions data_permissions_permission_id_set_id_key; Type: CONSTRAINT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.data_permissions
    ADD CONSTRAINT data_permissions_permission_id_set_id_key UNIQUE (permission_id, set_id);


--
-- Name: data_permissions data_permissions_pkey; Type: CONSTRAINT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.data_permissions
    ADD CONSTRAINT data_permissions_pkey PRIMARY KEY (id);


--
-- Name: datasets datasets_pkey; Type: CONSTRAINT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.datasets
    ADD CONSTRAINT datasets_pkey PRIMARY KEY (id);


--
-- Name: datasets datasets_set_id_tablename_colname_colval_key; Type: CONSTRAINT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.datasets
    ADD CONSTRAINT datasets_set_id_tablename_colname_colval_key UNIQUE (set_id, tablename, colname, colval);


--
-- Name: page_permissions page_permissions_permission_id_page_key; Type: CONSTRAINT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.page_permissions
    ADD CONSTRAINT page_permissions_permission_id_page_key UNIQUE (permission_id, page);


--
-- Name: page_permissions page_permissions_pkey; Type: CONSTRAINT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.page_permissions
    ADD CONSTRAINT page_permissions_pkey PRIMARY KEY (id);


--
-- Name: permissions permissions_code_permission_type_key; Type: CONSTRAINT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.permissions
    ADD CONSTRAINT permissions_code_permission_type_key UNIQUE (code, permission_type);


--
-- Name: permissions permissions_pkey; Type: CONSTRAINT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.permissions
    ADD CONSTRAINT permissions_pkey PRIMARY KEY (id);


--
-- Name: role_permissions role_permissions_pkey; Type: CONSTRAINT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.role_permissions
    ADD CONSTRAINT role_permissions_pkey PRIMARY KEY (id);


--
-- Name: role_permissions role_permissions_role_id_permission_id_key; Type: CONSTRAINT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.role_permissions
    ADD CONSTRAINT role_permissions_role_id_permission_id_key UNIQUE (role_id, permission_id);


--
-- Name: roles roles_code_key; Type: CONSTRAINT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.roles
    ADD CONSTRAINT roles_code_key UNIQUE (code);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- Name: sets sets_pkey; Type: CONSTRAINT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.sets
    ADD CONSTRAINT sets_pkey PRIMARY KEY (id);


--
-- Name: sets sets_setname_services_setcode_key; Type: CONSTRAINT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.sets
    ADD CONSTRAINT sets_setname_services_setcode_key UNIQUE (setname, services, setcode);


--
-- Name: social_providers social_providers_pkey; Type: CONSTRAINT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.social_providers
    ADD CONSTRAINT social_providers_pkey PRIMARY KEY (id);


--
-- Name: social_providers social_providers_provider_key; Type: CONSTRAINT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.social_providers
    ADD CONSTRAINT social_providers_provider_key UNIQUE (provider);


--
-- Name: url_permissions url_permissions_pkey; Type: CONSTRAINT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.url_permissions
    ADD CONSTRAINT url_permissions_pkey PRIMARY KEY (id);


--
-- Name: user_roles user_roles_pkey; Type: CONSTRAINT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.user_roles
    ADD CONSTRAINT user_roles_pkey PRIMARY KEY (id);


--
-- Name: user_roles user_roles_user_id_role_id_key; Type: CONSTRAINT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.user_roles
    ADD CONSTRAINT user_roles_user_id_role_id_key UNIQUE (user_id, role_id);


--
-- Name: user_totp user_totp_pkey; Type: CONSTRAINT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.user_totp
    ADD CONSTRAINT user_totp_pkey PRIMARY KEY (user_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: idx_access_request_items_req; Type: INDEX; Schema: uaa; Owner: admin
--

CREATE INDEX idx_access_request_items_req ON uaa.access_request_items USING btree (request_id);


--
-- Name: idx_access_request_logs_req; Type: INDEX; Schema: uaa; Owner: admin
--

CREATE INDEX idx_access_request_logs_req ON uaa.access_request_logs USING btree (request_id);


--
-- Name: idx_access_requests_requester; Type: INDEX; Schema: uaa; Owner: admin
--

CREATE INDEX idx_access_requests_requester ON uaa.access_requests USING btree (requester_id);


--
-- Name: idx_access_requests_status; Type: INDEX; Schema: uaa; Owner: admin
--

CREATE INDEX idx_access_requests_status ON uaa.access_requests USING btree (status);


--
-- Name: data_permissions data_permissions_set_id_fkey; Type: FK CONSTRAINT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.data_permissions
    ADD CONSTRAINT data_permissions_set_id_fkey FOREIGN KEY (set_id) REFERENCES uaa.sets(id) ON DELETE CASCADE;


--
-- Name: datasets datasets_set_id_fkey; Type: FK CONSTRAINT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.datasets
    ADD CONSTRAINT datasets_set_id_fkey FOREIGN KEY (set_id) REFERENCES uaa.sets(id) ON DELETE CASCADE;


--
-- Name: role_permissions role_permissions_role_id_fkey; Type: FK CONSTRAINT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.role_permissions
    ADD CONSTRAINT role_permissions_role_id_fkey FOREIGN KEY (role_id) REFERENCES uaa.roles(id) ON DELETE CASCADE;


--
-- Name: user_roles user_roles_role_id_fkey; Type: FK CONSTRAINT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.user_roles
    ADD CONSTRAINT user_roles_role_id_fkey FOREIGN KEY (role_id) REFERENCES uaa.roles(id) ON DELETE CASCADE;


--
-- Name: user_roles user_roles_user_id_fkey; Type: FK CONSTRAINT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.user_roles
    ADD CONSTRAINT user_roles_user_id_fkey FOREIGN KEY (user_id) REFERENCES uaa.users(id) ON DELETE CASCADE;


--
-- Name: user_totp user_totp_user_id_fkey; Type: FK CONSTRAINT; Schema: uaa; Owner: admin
--

ALTER TABLE ONLY uaa.user_totp
    ADD CONSTRAINT user_totp_user_id_fkey FOREIGN KEY (user_id) REFERENCES uaa.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

Cách restore file dump /tmp/uaa_dump.sql vào DB mới:

1. Tạo DB mới (ví dụ dev_uaa):
createdb -h localhost -U admin dev_uaa

2. Nạp dump:
psql -h localhost -U admin -d dev_uaa -f /tmp/uaa_dump.sql

3. Kiểm tra:
psql -h localhost -U admin -d dev_uaa -c '\dt uaa.*'

*Nếu cần đổi owner tất cả đối tượng sang user khác (ví dụ admin), sau khi restore chạy:
psql -h localhost -U admin -d dev_uaa -c "ALTER SCHEMA uaa OWNER TO admin; ALTER DATABASE dev_uaa OWNER TO admin;"
psql -h localhost -U admin -d dev_uaa -c "DO $$DECLARE r RECORD; BEGIN FOR r IN SELECT tablename FROM pg_tables WHERE schemaname='uaa' LOOP EXECUTE format('ALTER TABLE uaa.%I OWNER TO admin', r.tablename); END LOOP; END$$;"