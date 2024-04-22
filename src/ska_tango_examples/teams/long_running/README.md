# Long Running Command Sample Devices

## Introduction

This module includes various devices to illustrate how LRCs are used.

Two ways to keep track of task completion are also illustrated:
- `On` command inheriting from SlowCommand only, highlighting how much boilerplate code SubmittedSlowCommand saves.
- `Off` command inheriting from SubmittedSlowCommand. This is the recommended example to follow for long running commands.
Both `On` and `Off` leverage the task executor and command tracker built in to the base classes.

The examples include the usage of a component manager to encapsulate business logic.

## Device layout

                         Controller (test/lrccontroller/1)
                            |                         |
        Station(test/lrcstation/1)                Station(test/lrcstation/2)
                |           |                         |                  |
    Tile(test/lrctile/1)  Tile(test/lrctile/2)   Tile(test/lrctile/3)  Tile(test/lrctile/4)

On/Off commands propagate down from the Controller to Tile.

## Command flow

### `On` ( and `Off`)

  - #### _Controller_
    - Controller receives `On`
    - Controller subscribes to change event on Station attribute `longRunningCommandResult`
    - `On` is executed on Stations
    - Controller waits for Stations to send a `longRunningCommandResult` change event.
      - #### _Station_
        - Station receives `On`
        - Station subscribes to change event on Tile attribute `longRunningCommandResult`
        - `On` is executed on Tiles
        - Station waits for Tiles to send a `longRunningCommandResult` change event.
          - #### _Tile_
            - Tile goes to `On` state, sends `longRunningCommandResult` change event.
        - Station goes to `On` state, sends `longRunningCommandResult` change event.
    - Controller goes to `On` state (also sending a `longRunningCommandResult`).