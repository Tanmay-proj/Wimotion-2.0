from typing import List, Dict, Any


class PersonTracker:
    def __init__(self):
        self.next_id = 1
        self.previous = {}

    def update(self, detected_people: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        output = []
        used_ids = set()

        for person in detected_people:
            zone = person["zone"]
            existing_id = None

            for pid, old_zone in self.previous.items():
                if old_zone == zone and pid not in used_ids:
                    existing_id = pid
                    break

            if existing_id is None:
                existing_id = self.next_id
                self.next_id += 1

            used_ids.add(existing_id)
            output.append({
                "id": existing_id,
                "zone": zone
            })

        self.previous = {
            p["id"]: p["zone"]
            for p in output
        }

        return output

    def reset(self):
        self.next_id = 1
        self.previous.clear()
