# Long Running Command Sample Devices

## Introduction

This module includes various devices to illustrate how LRCs are used.

Two ways to keep track of task completion are also illustrated:
- `On`/`Off` commands waiting on state changes of subservient devices to determine command completion.
- `Scan` command using callbacks on attribute `longRunningCommandResult`of subservient devices to determine command completion.

The examples include the usage of a component manager to encapsulate business logic.

## Device layout

                         Controller (test/lrccontroller/1)
                            |                         |
        Station(test/lrcstation/1)                Station(test/lrcstation/2)
                |           |                         |                  |
    Tile(test/lrctile/1)  Tile(test/lrctile/2)   Tile(test/lrctile/3)  Tile(test/lrctile/4)

On/Off/Scan  commands propagate down from the Controller to Tile.

## Command flow

### `On` ( and `Off`)

  - #### _Controller_
    - Controller receives `On`
    - `On` is executed on Stations
    - Controller waits for Station state to change to `On`
      - #### _Station_
        - Station receives `On`
        - `On` is executed on Tiles
        - Station waits for Tile state to change to `On`
          - #### _Tile_
            - Tile goes to `On` state
        - Station goes to `On` state
    - Controller goes to `On` state

### `Scan`

  - #### _Controller_
    - Controller receives `Scan`
    - Component Manager set to `scanning`
    - Controller subscribes to change event on Station attribute `longRunningCommandResult`
    - `Scan` is executed on Stations
      - #### _Station_
        - Station receives `Scan`
        - Component Manager set to `scanning`
        - Station subscribes to change event on Tile attribute `longRunningCommandResult`
        - `Scan` is executed on Tiles
          - #### _Tile_
            - Tile receives `Scan`
            - `Scan` is completed, change event on `longRunningCommandResult`
        - Station receives change event on Tile result
        - Component Manager unsets `scanning`
    - Controller receives change event on Station result
    - Component Manager unsets `scanning`
