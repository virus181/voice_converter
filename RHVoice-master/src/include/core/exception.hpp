/* Copyright (C) 2012  Olga Yakovleva <yakovleva.o.v@gmail.com> */

/* This program is free software: you can redistribute it and/or modify */
/* it under the terms of the GNU Lesser General Public License as published by */
/* the Free Software Foundation, either version 2.1 of the License, or */
/* (at your option) any later version. */

/* This program is distributed in the hope that it will be useful, */
/* but WITHOUT ANY WARRANTY; without even the implied warranty of */
/* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the */
/* GNU Lesser General Public License for more details. */

/* You should have received a copy of the GNU Lesser General Public License */
/* along with this program.  If not, see <http://www.gnu.org/licenses/>. */

#ifndef RHVOICE_EXCEPTION_HPP
#define RHVOICE_EXCEPTION_HPP

#include <stdexcept>
#include <string>

namespace RHVoice
{
  class exception: public std::runtime_error
  {
  public:
    explicit exception(const std::string& msg):
      std::runtime_error(msg)
    {
    }
  };

  class lookup_error: public exception
  {
  public:
    explicit lookup_error(const std::string& msg):
      exception(msg)
    {
    }
  };

  class file_format_error: public exception
  {
  public:
    explicit file_format_error(const std::string& msg):
      exception(msg)
    {
    }
  };
}
#endif
