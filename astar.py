# ASTAR ########
def astar(source, target):
    obstacles = {}
    def g(start,neighbor):
        return 10 if start[0] == neighbor[0] or start[1] == neighbor[1] else 14
    def h(start,target):
        return 10 * (abs(start[0] - target[0]) + abs(start[1] - target[1]))
    def f(neighbor):
        previous_g = to_see[current]["g"]
        next_g = g(current,neighbor)
        next_h = h(neighbor,target)
        return { 
                "g": previous_g + next_g,
                "h": next_h, 
                "f": previous_g + next_g + next_h,
                "parent": current
               }
    def astar_print(node):
        final = [[node[0],node[1]]]
        current_node = node
        while True:
            if seen[current_node].get("parent"):
                final.append([seen[current_node].get("parent")[0], seen[current_node].get("parent")[1]])
                current_node = seen[current_node]["parent"]
            else:
                return final
    current = source
    to_see = dict()
    seen = dict()
    to_see.update({ current: { "g": 0, "h": h(current,target), "f": h(current,target) } })
    while current[:2] != target[:2]:
        seen.update({ current: to_see[current] })
        nbrs = [(current[0]+i, current[1]+j) for i in [-1,0,1] for j in [-1,0,1]]
        visit_nbrs = { x: f(x) for x in nbrs if x not in obstacles and x not in seen }
        del to_see[current]
        for k,v in visit_nbrs.items():
            if to_see.get(k):
                if v["g"] < to_see[k]["g"]:
                    to_see.update({ k: v })
            else:
                to_see.update({ k: v })
        to_see.update(visit_nbrs)
        current = min(visit_nbrs, key=lambda x: visit_nbrs[x]['f'])
    seen.update({ current: to_see[current] })
    r_path = astar_print(target)
    return r_path[::-1]
# ASTAR ########