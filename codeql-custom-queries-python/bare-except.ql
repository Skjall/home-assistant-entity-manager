/**
 * @name Bare except clauses
 * @description Finds bare except: statements that catch all exceptions
 * @kind problem
 * @problem.severity warning
 * @id python/bare-except
 * @tags reliability
 *       error-handling
 */

import python

from ExceptStmt e
where 
  not exists(e.getType()) and
  not e.getLocation().getFile().getRelativePath().matches("legacy/%") and
  not e.getLocation().getFile().getRelativePath().matches("venv%")
select e, "Bare 'except:' clause catches all exceptions - be more specific"