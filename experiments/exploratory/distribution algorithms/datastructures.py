import random


class Room:
    def __init__(self, label=None, capacity=None, room_type=None):
        if label is None:
            label = 'noLabel'
        if capacity is None:
            capacity = random.randint(1, 6)
        if room_type is None:
            room_type = random.choices(['male', 'female', 'free'], weights=[0.3, 0.25, 0.45])[0]
        self.label = label
        self.capacity = capacity
        self.room_type = room_type
        self.student_ids = []

    def __str__(self):
        return f"Room Label: {self.label}, Capacity: {self.capacity}, Type: {self.room_type}"

    def __lt__(self, other):
        if not isinstance(other, Room):
            raise ValueError("Can only compare with another Room object.")
        return self.size() < other.size()

    def init_randomly(self, capacity_range: (int, int), gender_distribution: (int, int, int) = (0.3, 0.25, 0.45)):
        self.capacity = random.randint(*capacity_range)
        self.label = 'noLabel'
        self.room_type = random.choices(['male', 'female', 'free'], weights=gender_distribution)[0]

    def size(self):
        return self.capacity - len(self.student_ids)


def create_random_room_list(people_count: int, capacity_range: (int, int) = (1, 5), room_type=None):
    left_people = people_count
    rooms = []
    while left_people > capacity_range[1]:
        room = Room()
        room.init_randomly(capacity_range=capacity_range)
        if room_type is not None:
            room.room_type = room_type
        rooms.append(room)
        left_people -= room.capacity
    rooms.append(Room(capacity=left_people))
    return rooms


def create_random_room_list_with_gender_distribution(male_female: (int, int), capacity_range: (int, int) = (1, 5)):
    rooms_male = create_random_room_list(male_female[0], capacity_range, room_type="male")
    rooms_female = create_random_room_list(male_female[1], capacity_range, room_type="female")
    return rooms_male + rooms_female
