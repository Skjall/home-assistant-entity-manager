/**
 * @name Home Assistant token exposure in logs
 * @description Detects potential exposure of HA tokens in log statements
 * @kind problem
 * @problem.severity error
 * @id python/ha-token-exposure
 * @tags security
 *       home-assistant
 */

import python

from Call c, StrConst s
where 
  (
    c.getFunc().(Attribute).getName() in ["info", "debug", "warning", "error", "critical"] or
    c.getFunc().(Name).getId() = "print"
  ) and
  s = c.getAnArg() and
  (
    s.getText().regexpMatch(".*[Tt]oken.*") or
    s.getText().regexpMatch(".*[Bb]earer.*") or
    s.getText().regexpMatch(".*[Aa]uthorization.*") or
    s.getText().regexpMatch(".*[Aa]pi_?[Kk]ey.*") or
    s.getText().regexpMatch(".*SUPERVISOR_TOKEN.*")
  ) and
  not c.getLocation().getFile().getRelativePath().matches("legacy/%")
select c, "Potential token/secret exposure in log statement: " + s.getText()