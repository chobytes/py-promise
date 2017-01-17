from functools import reduce


"""
    Dependent method container. Holds onto handler functions to be run upon promise resolution.

    Example usage:

    def myErrorHandler(e):
        ...

    def mySuccessHanlder(v):
        ...

    newDependent = Depedent(mySuccessHanlder, myErrorHandler)
    somePromise.dependents.append(newDependent)
"""
class Dependent(object):
    def __init__(self, success, fail):
        self.fulfilled = success
        self.rejected = fail




"""
    Promise object for composing computations that make fail, and/or async computations.
    Example usage:

    def makePromise():
        p = Promise()
        result = 2 + 2
            if 2 + 2 == 4:
                p.resolve(result)
            else:
                p.reject("ERROR: You broke math")
        return p
"""
class Promise(object):
    def __init__(self):
        self.value = None # Initial promise value
        self.status = "PENDING" # All promises start out pending
        self.dependents = [] # Dependent Objects go here
        self.executedDependents = [] # Resulting promises from executed dependents go here



    """ Mark promise fulfilled, or rejected. If applicable runs appropriate handler method on all dependent computations. """
    def fulfill(self, value):
        if self.status == "PENDING":
            self.status = "FULFILLED"
            self.value = value
            if len(self.dependents) > 0:
                deps = self.dependents
                self.dependents = []
                ed = reduce(lambda acc, d: acc.append(d.fulfilled(value)), deps, [])
                self.executedDependents.append(ed)
        else:
            exc = "Attempting to fulfill already {status} promise. Attempting to fulfill with {newV}" \
            .format(status = self.getStatus(), newV = value)
            raise Exception(exc)
        return self

    def reject(self, err):
        if not self.status == "REJECRED":
            self.status = "REJECTED"
            self.value = err
            if len(self.dependents) > 0:
                deps = self.dependents
                self.dependents = []
                ed = reduce(lambda acc, d: acc.append(d.rejected(err)), deps, [])
                self.executedDependents.append(ed)
        else:
            exc = "Attempig to reject an already {status} promise. Current error {curErr}. New error {newErr}." \
            .format(status = self.getStatus(), newErr = err)
            raise Exception(exc)
        return self





    """Add new dependent to promise. If promise is complete, run immediatly instead"""
    def then(self, success, failure = "MISSING"):
        result = Promise()

        """If no failure handler is present, pass the error on in a rejected promise"""
        if failure == "MISSING":
            failure = lambda e: Promise().reject(e)

        """Update status of this promise with result of success or failure"""
        def hook(p):
            """Ensure p is a promise"""
            def wrap(p):
                if not isinstance(p, Promise):
                    p = Promise().fulfill(p)
                return p
            def s(newV):
                result.fulfill(newV)
                return Promise()
            def f(newE):
                result.reject(newE)
                return Promise()
            return wrap(p).then(s, f)

        """If promise is pending, append as dependent. Otherwise run immediately"""
        if self.status == "PENDING":
            def fulfilled(value):
                hook(success(value))
            def rejected(e):
                hook(failure(e))
            newDependent = Dependent(fulfilled, rejected)
            self.dependents.append(newDependent)
        elif self.status == "FULFILLED":
            hook(success(self.value))
        elif self.status == "REJECTED":
            hook(failure(self.value))
        else:
            exc = "Failure attempting to append {curDep}. Append not defined for case of {curStatus}." \
            .format(curDep = (success, failure), curStatus = self.getStatus)
            raise Exception(exc)

        return result




    """Returns status of promise."""
    def getStatus(self):
        return self.status
