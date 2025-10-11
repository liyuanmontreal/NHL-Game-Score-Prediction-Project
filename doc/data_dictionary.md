# 🏒 NHL Game JSON Data Dictionary  

This document describes the structure and meaning of the fields in NHL game play-by-play JSON files.
本文档说明 NHL 官方比赛逐场（Play-by-Play）数据 JSON 文件中各字段的含义，  包括顶层元数据、球队信息、时钟、比赛事件（plays）及事件细节（details）。

---

##  1. Top-Level Structure 顶层结构

| Key | Type | Description (EN) | 说明 (中文) |
|-----|------|------------------|-------------|
| `id` | integer | Unique game identifier assigned by NHL. | 比赛唯一编号。 |
| `season` | integer | Season ID (e.g., `20222023` for the 2022–23 season). | 赛季编号。 |
| `gameType` | integer | Game type (1=Preseason, 2=Regular, 3=Playoffs). | 比赛类型（1=季前赛，2=常规赛，3=季后赛）。 |
| `limitedScoring` | boolean | Indicates if scoring data is restricted. | 是否限制得分统计。 |
| `gameDate` | string | Official game date in ISO format (UTC). | 比赛日期（ISO 格式，UTC）。 |
| `venue` | object | Venue name information. | 比赛场馆名称。 |
| `venueLocation` | object | City and location of the venue. | 场馆所在城市与位置。 |
| `startTimeUTC` | string | Game start time (UTC). | 比赛开始时间（UTC）。 |
| `easternUTCOffset` | string | Eastern time zone offset. | 东部时区偏移。 |
| `venueUTCOffset` | string | Venue local time offset. | 场馆本地时区偏移。 |
| `tvBroadcasts` | array | List of TV broadcast details (network, country, language). | 播出信息（电视台、国家、语言）。 |
| `gameState` | string | Current state (`OFF`=Finished, `LIVE`=Ongoing, `FUT`=Scheduled). | 当前比赛状态（OFF=结束，LIVE=进行中，FUT=未来）。 |
| `gameScheduleState` | string | Schedule state (usually `OK`). | 赛程状态。 |
| `periodDescriptor` | object | Description of current or final period. | 当前或最后一节的信息。 |
| `awayTeam` | object | Away team details (see below). | 客队信息（见下）。 |
| `homeTeam` | object | Home team details (see below). | 主队信息（见下）。 |
| `shootoutInUse` | boolean | Whether shootout was used. | 是否使用点球大战。 |
| `otInUse` | boolean | Whether overtime was used. | 是否使用加时赛。 |
| `clock` | object | Real-time clock information. | 比赛计时器状态。 |
| `displayPeriod` | integer | Current or final period number. | 当前显示的比赛节数。 |
| `gameOutcome` | object | Outcome descriptor (e.g., lastPeriodType). | 比赛结果信息。 |
| `plays` | array | List of all game events (play-by-play). | 比赛事件记录列表（逐场动作）。 |

---

##  2. Team Object 球队信息（`homeTeam` / `awayTeam`）

| Key | Type | Description (EN) | 说明 (中文) |
|-----|------|------------------|-------------|
| `id` | integer | NHL internal team ID. | 球队官方编号。 |
| `commonName.default` | string | Team’s short common name. | 球队常用名（例如 "Panthers"）。 |
| `abbrev` | string | Three-letter abbreviation. | 球队缩写（如 "FLA"）。 |
| `score` | integer | Final score. | 最终比分。 |
| `sog` | integer | Total shots on goal. | 射门次数。 |
| `logo` | string | URL to team logo (light background). | 球队 LOGO 链接。 |
| `darkLogo` | string | URL to team logo (dark background). | 深色背景版 LOGO。 |
| `placeName.default` | string | Team city or region name. | 球队所属城市。 |
| `placeNameWithPreposition.default` | string | City name with preposition (for French). | 带介词的城市名称（法语显示用）。 |

---

##  3. Clock Object 比赛计时器

| Key | Type | Description (EN) | 说明 (中文) |
|-----|------|------------------|-------------|
| `timeRemaining` | string | Remaining time in period (MM:SS). | 当前节剩余时间（分钟:秒）。 |
| `secondsRemaining` | integer | Remaining seconds. | 当前节剩余秒数。 |
| `running` | boolean | Whether clock is running. | 时钟是否在运行中。 |
| `inIntermission` | boolean | Whether the game is in intermission. | 是否处于节间休息。 |

---

##  4. Plays Object 比赛事件列表

Each play (event) represents a specific action (shot, goal, penalty, hit, etc.).  
每个 play 表示比赛中的一个具体事件，如射门、进球、犯规、撞击等。

| Key | Type | Description (EN) | 说明 (中文) |
|-----|------|------------------|-------------|
| `eventId` | integer | Unique event ID. | 事件唯一编号。 |
| `periodDescriptor.number` | integer | Period number (1–3 or OT). | 比赛节次（1–3 或加时 OT）。 |
| `periodDescriptor.periodType` | string | Period type (`REG`, `OT`, etc.). | 节类型（常规、加时等）。 |
| `timeInPeriod` | string | Time elapsed in current period (MM:SS). | 当前节内事件发生时间（分:秒）。 |
| `timeRemaining` | string | Remaining time in period. | 该节剩余时间。 |
| `situationCode` | string | Player situation code (e.g., 1551 = 5v5). | 场上人数状态（如 1551 表示 5 对 5）。 |
| `homeTeamDefendingSide` | string | Indicates home team defensive side (`left` / `right`). | 主队防守方向。 |
| `typeCode` | integer | Internal event type code. | 事件类型编号。 |
| `typeDescKey` | string | Text key for event type (e.g., `goal`, `shot-on-goal`). | 事件类型（如 goal、shot-on-goal）。 |
| `sortOrder` | integer | Sort index for chronological order. | 时间顺序索引。 |
| `teamName` | string | Team performing the event. | 执行事件的球队名称。 |
| `details` | object | Event details (depends on event type). | 事件细节（根据类型不同而变化）。 |

---

##  5. Details Object 事件细节（随类型变化）

### 🔹 Common Fields 通用字段

| Key | Type | Description (EN) | 说明 (中文) |
|-----|------|------------------|-------------|
| `xCoord` | float | X-coordinate on ice surface (in feet). | 冰场 X 坐标（英尺）。 |
| `yCoord` | float | Y-coordinate on ice surface (in feet). | 冰场 Y 坐标（英尺）。 |
| `zoneCode` | string | Zone of play (`O`=Offensive, `D`=Defensive, `N`=Neutral). | 区域类型：O=进攻区，D=防守区，N=中立区。 |

---

### 🔹 Shot-on-Goal Event 射门事件
| Key | Description (EN) | 说明 (中文) |
|-----|------------------|-------------|
| `shotType` | Type of shot (e.g., wrist, slap, backhand). | 射门类型（腕射、击射、反手等）。 |
| `shootingPlayerId` | ID of shooting player. | 射门球员 ID。 |
| `goalieInNetId` | Goalie’s player ID. | 当前守门员 ID。 |
| `eventOwnerTeamId` | Team ID that performed the event. | 执行该事件的球队 ID。 |
| `awaySOG` / `homeSOG` | Shots on goal count for each team at this time. | 当前时刻客队/主队射门数。 |

---

### 🔹 Goal Event 进球事件
| Key | Description (EN) | 说明 (中文) |
|-----|------------------|-------------|
| `scoringPlayerId` | Player ID of scorer. | 进球球员 ID。 |
| `assist1PlayerId` / `assist2PlayerId` | IDs of assisting players. | 助攻球员 ID。 |
| `awayScore` / `homeScore` | Updated scores after goal. | 进球后的比分。 |
| `shotType` | Type of shot that led to the goal. | 进球的射门类型。 |
| `goalieInNetId` | Goalie facing the shot. | 当时守门员 ID。 |
| `strength` | Play strength (e.g., `EVEN`, `PPG`, `SHG`). | 比赛强度状态（如多打少、少防多）。 |

---

### 🔹 Penalty Event 犯规事件
| Key | Description (EN) | 说明 (中文) |
|-----|------------------|-------------|
| `typeCode` | Internal penalty type code. | 犯规类型编号。 |
| `descKey` | Penalty description (e.g., tripping, high-sticking). | 犯规描述。 |
| `duration` | Penalty duration in minutes. | 犯规时长（分钟）。 |
| `committedByPlayerId` | ID of player committing penalty. | 犯规球员 ID。 |
| `drawnByPlayerId` | ID of player drawing penalty. | 被犯规球员 ID。 |

---

### 🔹 Faceoff Event 开球事件
| Key | Description (EN) | 说明 (中文) |
|-----|------------------|-------------|
| `winningPlayerId` | ID of player who won faceoff. | 赢得开球的球员 ID。 |
| `losingPlayerId` | ID of losing player. | 输掉开球的球员 ID。 |
| `zoneCode` | Zone of the faceoff. | 开球所在区域。 |

---

### 🔹 Hit / Blocked Shot / Giveaway / Takeaway
| Key | Description (EN) | 说明 (中文) |
|-----|------------------|-------------|
| `hittingPlayerId` / `hitteePlayerId` | Players involved in hit. | 撞击双方球员 ID。 |
| `blockingPlayerId` | Blocking player ID. | 封堵射门球员。 |
| `shootingPlayerId` | Shooter in blocked shot event. | 被封射门者。 |
| `playerId` | Player performing takeaway/giveaway. | 抢断/失误的球员 ID。 |

---

##  6. Coordinates & Zones 坐标系统

| Term | Description (EN) | 说明 (中文) |
|------|------------------|-------------|
| `(0, 0)` | Center of the rink. | 冰场中心点。 |
| `xCoord` | Increases toward the attacking net. | x 坐标增大方向为进攻方向。 |
| `yCoord` | Positive toward right-side boards. | y 坐标正值为右侧。 |
| `zoneCode` | `O` (Offensive), `D` (Defensive), `N` (Neutral). | 进攻区、防守区、中立区标识。 |

---

##  7. Example 示例

```json
{
  "typeDescKey": "goal",
  "details": {
    "scoringPlayerId": 8477934,
    "assist1PlayerId": 8474565,
    "awayScore": 1,
    "homeScore": 0,
    "xCoord": 93,
    "yCoord": -5
  }
}
