/**
 * @name WebSocket connection without authentication check
 * @description Detects WebSocket handlers that don't verify authentication
 * @kind problem
 * @problem.severity error
 * @id python/websocket-no-auth
 * @tags security
 *       authentication
 */

import python

from Function f, string fname
where
  fname = f.getName() and
  (
    fname.matches("%websocket%") or
    fname.matches("%ws_%") or
    f.getADecorator().(Attribute).getName() = "websocket"
  ) and
  not exists(string s | 
    s = f.getAStmt().toString() and
    (
      s.matches("%auth%") or
      s.matches("%token%") or
      s.matches("%authenticate%") or
      s.matches("%verify%")
    )
  ) and
  not f.getLocation().getFile().getRelativePath().matches("legacy/%") and
  not f.getLocation().getFile().getRelativePath().matches("tests/%")
select f, "WebSocket handler without apparent authentication check"