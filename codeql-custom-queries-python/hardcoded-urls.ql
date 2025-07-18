/**
 * @name Hardcoded URLs
 * @description Finds hardcoded HTTP/HTTPS URLs in the code
 * @kind problem
 * @problem.severity warning
 * @id python/hardcoded-urls
 * @tags maintainability
 */

import python

from StrConst s
where 
  s.getText().regexpMatch("https?://.*") and
  not s.getLocation().getFile().getRelativePath().matches("legacy/%")
select s, "Hardcoded URL found: " + s.getText()