--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: dns_server; Type: TABLE; Schema: public; Owner: passivedns; Tablespace: 
--

CREATE TABLE dns_server (
    dns_server_id bigint NOT NULL,
    entry_id bigint,
    ip cidr,
    first_seen timestamp without time zone,
    last_seen timestamp without time zone,
    count bigint
);


ALTER TABLE public.dns_server OWNER TO passivedns;

--
-- Name: dns_server_dns_server_id_seq; Type: SEQUENCE; Schema: public; Owner: passivedns
--

CREATE SEQUENCE dns_server_dns_server_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dns_server_dns_server_id_seq OWNER TO passivedns;

--
-- Name: dns_server_dns_server_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: passivedns
--

ALTER SEQUENCE dns_server_dns_server_id_seq OWNED BY dns_server.dns_server_id;


--
-- Name: domain; Type: TABLE; Schema: public; Owner: passivedns; Tablespace: 
--

CREATE TABLE domain (
    domain_id bigint NOT NULL,
    parent_domain_id bigint,
    domain_name character varying(255) NOT NULL
);


ALTER TABLE public.domain OWNER TO passivedns;

--
-- Name: domain_domain_id_seq; Type: SEQUENCE; Schema: public; Owner: passivedns
--

CREATE SEQUENCE domain_domain_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.domain_domain_id_seq OWNER TO passivedns;

--
-- Name: domain_domain_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: passivedns
--

ALTER SEQUENCE domain_domain_id_seq OWNED BY domain.domain_id;


--
-- Name: entry; Type: TABLE; Schema: public; Owner: passivedns; Tablespace: 
--

CREATE TABLE entry (
    entry_id bigint NOT NULL,
    domain_id bigint,
    type smallint,
    ttl bigint,
    value character varying(255) NOT NULL,
    first_seen timestamp without time zone,
    last_seen timestamp without time zone,
    count bigint
);


ALTER TABLE public.entry OWNER TO passivedns;

--
-- Name: entry_entry_id_seq; Type: SEQUENCE; Schema: public; Owner: passivedns
--

CREATE SEQUENCE entry_entry_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.entry_entry_id_seq OWNER TO passivedns;

--
-- Name: entry_entry_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: passivedns
--

ALTER SEQUENCE entry_entry_id_seq OWNED BY entry.entry_id;


--
-- Name: parent_domain; Type: TABLE; Schema: public; Owner: passivedns; Tablespace: 
--

CREATE TABLE parent_domain (
    parent_domain_id bigint NOT NULL,
    parent_domain_name character varying(255) NOT NULL
);


ALTER TABLE public.parent_domain OWNER TO passivedns;

--
-- Name: parent_domain_parent_domain_id_seq; Type: SEQUENCE; Schema: public; Owner: passivedns
--

CREATE SEQUENCE parent_domain_parent_domain_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.parent_domain_parent_domain_id_seq OWNER TO passivedns;

--
-- Name: parent_domain_parent_domain_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: passivedns
--

ALTER SEQUENCE parent_domain_parent_domain_id_seq OWNED BY parent_domain.parent_domain_id;


--
-- Name: sensor; Type: TABLE; Schema: public; Owner: passivedns; Tablespace: 
--

CREATE TABLE sensor (
    sensor_id bigint NOT NULL,
    sensor_name character varying(64)
);


ALTER TABLE public.sensor OWNER TO passivedns;

--
-- Name: sensor_domain; Type: TABLE; Schema: public; Owner: passivedns; Tablespace: 
--

CREATE TABLE sensor_domain (
    domain_id bigint NOT NULL,
    sensor_id bigint NOT NULL,
    first_seen timestamp without time zone,
    last_seen timestamp without time zone
);


ALTER TABLE public.sensor_domain OWNER TO passivedns;

--
-- Name: sensor_sensor_id_seq; Type: SEQUENCE; Schema: public; Owner: passivedns
--

CREATE SEQUENCE sensor_sensor_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sensor_sensor_id_seq OWNER TO passivedns;

--
-- Name: sensor_sensor_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: passivedns
--

ALTER SEQUENCE sensor_sensor_id_seq OWNED BY sensor.sensor_id;


--
-- Name: dns_server_id; Type: DEFAULT; Schema: public; Owner: passivedns
--

ALTER TABLE ONLY dns_server ALTER COLUMN dns_server_id SET DEFAULT nextval('dns_server_dns_server_id_seq'::regclass);


--
-- Name: domain_id; Type: DEFAULT; Schema: public; Owner: passivedns
--

ALTER TABLE ONLY domain ALTER COLUMN domain_id SET DEFAULT nextval('domain_domain_id_seq'::regclass);


--
-- Name: entry_id; Type: DEFAULT; Schema: public; Owner: passivedns
--

ALTER TABLE ONLY entry ALTER COLUMN entry_id SET DEFAULT nextval('entry_entry_id_seq'::regclass);


--
-- Name: parent_domain_id; Type: DEFAULT; Schema: public; Owner: passivedns
--

ALTER TABLE ONLY parent_domain ALTER COLUMN parent_domain_id SET DEFAULT nextval('parent_domain_parent_domain_id_seq'::regclass);


--
-- Name: sensor_id; Type: DEFAULT; Schema: public; Owner: passivedns
--

ALTER TABLE ONLY sensor ALTER COLUMN sensor_id SET DEFAULT nextval('sensor_sensor_id_seq'::regclass);


--
-- Name: dns_server_pkey; Type: CONSTRAINT; Schema: public; Owner: passivedns; Tablespace: 
--

ALTER TABLE ONLY dns_server
    ADD CONSTRAINT dns_server_pkey PRIMARY KEY (dns_server_id);


--
-- Name: domain_pkey; Type: CONSTRAINT; Schema: public; Owner: passivedns; Tablespace: 
--

ALTER TABLE ONLY domain
    ADD CONSTRAINT domain_pkey PRIMARY KEY (domain_id);


--
-- Name: entry_pkey; Type: CONSTRAINT; Schema: public; Owner: passivedns; Tablespace: 
--

ALTER TABLE ONLY entry
    ADD CONSTRAINT entry_pkey PRIMARY KEY (entry_id);


--
-- Name: parent_domain_pkey; Type: CONSTRAINT; Schema: public; Owner: passivedns; Tablespace: 
--

ALTER TABLE ONLY parent_domain
    ADD CONSTRAINT parent_domain_pkey PRIMARY KEY (parent_domain_id);


--
-- Name: sensor_domain_pkey; Type: CONSTRAINT; Schema: public; Owner: passivedns; Tablespace: 
--

ALTER TABLE ONLY sensor_domain
    ADD CONSTRAINT sensor_domain_pkey PRIMARY KEY (domain_id, sensor_id);


--
-- Name: sensor_pkey; Type: CONSTRAINT; Schema: public; Owner: passivedns; Tablespace: 
--

ALTER TABLE ONLY sensor
    ADD CONSTRAINT sensor_pkey PRIMARY KEY (sensor_id);


--
-- Name: sensor_sensor_name_key; Type: CONSTRAINT; Schema: public; Owner: passivedns; Tablespace: 
--

ALTER TABLE ONLY sensor
    ADD CONSTRAINT sensor_sensor_name_key UNIQUE (sensor_name);


--
-- Name: fki_dns_server_entry; Type: INDEX; Schema: public; Owner: passivedns; Tablespace: 
--

CREATE INDEX fki_dns_server_entry ON dns_server USING btree (entry_id);


--
-- Name: fki_domain_parent_domain; Type: INDEX; Schema: public; Owner: passivedns; Tablespace: 
--

CREATE INDEX fki_domain_parent_domain ON domain USING btree (parent_domain_id);


--
-- Name: fki_entry_domain; Type: INDEX; Schema: public; Owner: passivedns; Tablespace: 
--

CREATE INDEX fki_entry_domain ON entry USING btree (domain_id);


--
-- Name: fki_sensor_domain_domain; Type: INDEX; Schema: public; Owner: passivedns; Tablespace: 
--

CREATE INDEX fki_sensor_domain_domain ON sensor_domain USING btree (domain_id);


--
-- Name: fki_sensor_domain_sensor; Type: INDEX; Schema: public; Owner: passivedns; Tablespace: 
--

CREATE INDEX fki_sensor_domain_sensor ON sensor_domain USING btree (sensor_id);


--
-- Name: search index; Type: INDEX; Schema: public; Owner: passivedns; Tablespace: 
--

CREATE UNIQUE INDEX "search index" ON entry USING btree (domain_id, type, ttl, value);


--
-- Name: fk_dns_server_entry; Type: FK CONSTRAINT; Schema: public; Owner: passivedns
--

ALTER TABLE ONLY dns_server
    ADD CONSTRAINT fk_dns_server_entry FOREIGN KEY (entry_id) REFERENCES entry(entry_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: fk_domain_parent_domain; Type: FK CONSTRAINT; Schema: public; Owner: passivedns
--

ALTER TABLE ONLY domain
    ADD CONSTRAINT fk_domain_parent_domain FOREIGN KEY (parent_domain_id) REFERENCES parent_domain(parent_domain_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: fk_entry_domain; Type: FK CONSTRAINT; Schema: public; Owner: passivedns
--

ALTER TABLE ONLY entry
    ADD CONSTRAINT fk_entry_domain FOREIGN KEY (domain_id) REFERENCES domain(domain_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: fk_sensor_domain_domain; Type: FK CONSTRAINT; Schema: public; Owner: passivedns
--

ALTER TABLE ONLY sensor_domain
    ADD CONSTRAINT fk_sensor_domain_domain FOREIGN KEY (domain_id) REFERENCES domain(domain_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: fk_sensor_domain_sensor; Type: FK CONSTRAINT; Schema: public; Owner: passivedns
--

ALTER TABLE ONLY sensor_domain
    ADD CONSTRAINT fk_sensor_domain_sensor FOREIGN KEY (sensor_id) REFERENCES sensor(sensor_id);


--
-- PostgreSQL database dump complete
--

