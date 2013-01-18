--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET search_path = public, pg_catalog;
SET default_tablespace = '';
SET default_with_oids = false;


CREATE USER passivedns  WITH ENCRYPTED PASSWORD 'password';
GRANT CONNECT ON DATABASE passivedns to passivedns;
CREATE USER passivedns_ro  WITH ENCRYPTED PASSWORD 'password';
GRANT CONNECT ON DATABASE passivedns to passivedns_ro;

--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- Name: dns_server; Type: ACL; Schema: public; Owner: passivedns
--

REVOKE ALL ON TABLE dns_server FROM PUBLIC;
REVOKE ALL ON TABLE dns_server FROM passivedns;
GRANT ALL ON TABLE dns_server TO passivedns;
GRANT SELECT ON TABLE dns_server TO passivedns_ro;


--
-- Name: dns_server_dns_server_id_seq; Type: ACL; Schema: public; Owner: passivedns
--

REVOKE ALL ON SEQUENCE dns_server_dns_server_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE dns_server_dns_server_id_seq FROM passivedns;
GRANT ALL ON SEQUENCE dns_server_dns_server_id_seq TO passivedns;


--
-- Name: domain; Type: ACL; Schema: public; Owner: passivedns
--

REVOKE ALL ON TABLE domain FROM PUBLIC;
REVOKE ALL ON TABLE domain FROM passivedns;
GRANT ALL ON TABLE domain TO passivedns;
GRANT SELECT ON TABLE domain TO passivedns_ro;


--
-- Name: domain_domain_id_seq; Type: ACL; Schema: public; Owner: passivedns
--

REVOKE ALL ON SEQUENCE domain_domain_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE domain_domain_id_seq FROM passivedns;
GRANT ALL ON SEQUENCE domain_domain_id_seq TO passivedns;


--
-- Name: entry; Type: ACL; Schema: public; Owner: passivedns
--

REVOKE ALL ON TABLE entry FROM PUBLIC;
REVOKE ALL ON TABLE entry FROM passivedns;
GRANT ALL ON TABLE entry TO passivedns;
GRANT SELECT ON TABLE entry TO passivedns_ro;


--
-- Name: entry_entry_id_seq; Type: ACL; Schema: public; Owner: passivedns
--

REVOKE ALL ON SEQUENCE entry_entry_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE entry_entry_id_seq FROM passivedns;
GRANT ALL ON SEQUENCE entry_entry_id_seq TO passivedns;


--
-- Name: parent_domain; Type: ACL; Schema: public; Owner: passivedns
--

REVOKE ALL ON TABLE parent_domain FROM PUBLIC;
REVOKE ALL ON TABLE parent_domain FROM passivedns;
GRANT ALL ON TABLE parent_domain TO passivedns;
GRANT SELECT ON TABLE parent_domain TO passivedns_ro;


--
-- Name: parent_domain.parent_domain_id; Type: ACL; Schema: public; Owner: passivedns
--

REVOKE ALL(parent_domain_id) ON TABLE parent_domain FROM PUBLIC;
REVOKE ALL(parent_domain_id) ON TABLE parent_domain FROM passivedns;
GRANT ALL(parent_domain_id) ON TABLE parent_domain TO passivedns;


--
-- Name: parent_domain.parent_domain_name; Type: ACL; Schema: public; Owner: passivedns
--

REVOKE ALL(parent_domain_name) ON TABLE parent_domain FROM PUBLIC;
REVOKE ALL(parent_domain_name) ON TABLE parent_domain FROM passivedns;
GRANT ALL(parent_domain_name) ON TABLE parent_domain TO passivedns;


--
-- Name: parent_domain_parent_domain_id_seq; Type: ACL; Schema: public; Owner: passivedns
--

REVOKE ALL ON SEQUENCE parent_domain_parent_domain_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE parent_domain_parent_domain_id_seq FROM passivedns;
GRANT ALL ON SEQUENCE parent_domain_parent_domain_id_seq TO passivedns;


--
-- Name: sensor; Type: ACL; Schema: public; Owner: passivedns
--

REVOKE ALL ON TABLE sensor FROM PUBLIC;
REVOKE ALL ON TABLE sensor FROM passivedns;
GRANT ALL ON TABLE sensor TO passivedns;
GRANT SELECT ON TABLE sensor TO passivedns_ro;


--
-- Name: sensor_domain; Type: ACL; Schema: public; Owner: passivedns
--

REVOKE ALL ON TABLE sensor_domain FROM PUBLIC;
REVOKE ALL ON TABLE sensor_domain FROM passivedns;
GRANT ALL ON TABLE sensor_domain TO passivedns;
GRANT SELECT ON TABLE sensor_domain TO passivedns_ro;


--
-- Name: sensor_sensor_id_seq; Type: ACL; Schema: public; Owner: passivedns
--

REVOKE ALL ON SEQUENCE sensor_sensor_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE sensor_sensor_id_seq FROM passivedns;
GRANT ALL ON SEQUENCE sensor_sensor_id_seq TO passivedns;


--
-- PostgreSQL database dump complete
--

