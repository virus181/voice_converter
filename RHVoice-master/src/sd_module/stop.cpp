/* Copyright (C) 2012  Olga Yakovleva <yakovleva.o.v@gmail.com> */

/* This program is free software: you can redistribute it and/or modify */
/* it under the terms of the GNU General Public License as published by */
/* the Free Software Foundation, either version 2 of the License, or */
/* (at your option) any later version. */

/* This program is distributed in the hope that it will be useful, */
/* but WITHOUT ANY WARRANTY; without even the implied warranty of */
/* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the */
/* GNU General Public License for more details. */

/* You should have received a copy of the GNU General Public License */
/* along with this program.  If not, see <http://www.gnu.org/licenses/>. */

#include "stop.hpp"
#include "state.hpp"

namespace RHVoice
{
  namespace sd
  {
    namespace cmd
    {
      action_t stop::execute()
      {
        state s;
        if(s.test(state::speaking))
          {
            s.clear(state::pausing);
            s.clear(state::paused);
            s.set(state::stopped);
          }
        return action_continue;
      }
    }
  }
}
