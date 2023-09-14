from maeve.util import Util
import inspect


class FunctionPipeline:

    def run(self, obj=None, attrs=None):
        args = attrs.get("args", [])
        kwargs = attrs.get("kwargs", {})

        try:
            func = getattr(self, attrs['function'])
        except AttributeError:
            raise AttributeError("No function in namespace called: {}".format(attrs['function']))

        sig = inspect.signature(func)
        if "obj" not in sig.parameters:
            try:
                func(*args, **kwargs)
                return obj
            except Exception as e:
                _ = self.handle_func_fail(attrs, e)
                return obj
        else:
            try:
                return func(obj, *args, **kwargs)
            except Exception as e:
                _ = self.handle_func_fail(attrs, e)
                return obj


    def handle_func_fail(self, attrs, e, ret=None):
        if attrs.get("fail_silently", False):
            self.log.info(
                "Marty pipeline function {} failed with error {}".format(attrs['function'], e)
            )
            return ret
        else:
            raise RuntimeError("Marty pipeline function {} failed".format(attrs['function'])) from e