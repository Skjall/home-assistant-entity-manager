/**
 * @name Unsafe JSON deserialization
 * @description Detects usage of json.load/loads without proper error handling
 * @kind problem
 * @problem.severity warning
 * @id python/unsafe-json-load
 * @tags reliability
 *       error-handling
 */

import python

from Call c
where
  c.getFunc().(Attribute).getName() in ["load", "loads"] and
  c.getFunc().(Attribute).getObject().(Name).getId() = "json" and
  not exists(Try t | c.getScope() = t.getAStmt().getScope()) and
  not c.getLocation().getFile().getRelativePath().matches("legacy/%")
select c, "JSON deserialization without proper error handling"