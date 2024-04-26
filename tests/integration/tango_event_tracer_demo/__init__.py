"""A set of Demo tests using ::class::`TangoEventTracer`.

Testing Tango occasionally requires waiting for events to occur and
then checking that the device is in the correct state. A naive approach
to do that would be to rely on things like:

- custom nested `while` loops combined with `time.sleep` statements to wait
    for events to occur
- explicit `subscribe_event` calls to register event listeners, and then
    check that the event was received

This approach has several drawbacks. Essentially, it introduces a lot of
boilerplate code, made by nested logic repeated in multiple test cases
and test modules in similar but never identical ways. This makes the code
less readable, harder to maintain, and more error-prone.

::class::`TangoEventTracer` aims to provide a more general, reusable, elegant
and OOP-friendly way to handle these scenarios. In this module we provide some
examples of how to use it to test some demo devices.

Note for who read this: this is just an experiment, everything is work in
progress and subject to change. We are using this repo just because it is
easy to work with it.
"""
